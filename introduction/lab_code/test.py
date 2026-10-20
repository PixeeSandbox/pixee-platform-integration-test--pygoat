from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def fake_render(self, request, template_name, context=None, *args, **kwargs):
        return HttpResponse((context or {}).get("output", ""))

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.render", side_effect=self.fake_render) as mock_render, \
                patch("introduction.views.subprocess.Popen") as mock_popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.content, b"Something went wrong")
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )

    def test_cmd_lab_uses_list_arguments_without_shell(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.render", side_effect=self.fake_render), \
                patch("introduction.views.subprocess.Popen") as mock_popen:
            mock_popen.return_value.communicate.return_value = (b"lookup output", b"")
            response = views.cmd_lab(request)

        self.assertEqual(response.content, b"lookup output")
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
