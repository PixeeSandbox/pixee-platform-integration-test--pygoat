from types import SimpleNamespace
from unittest.mock import ANY, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_valid_post_uses_argument_list_and_shell_false(self, mock_popen, mock_render):
        process = SimpleNamespace(communicate=lambda: (b"answer", b""))
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")
        request = self.factory.post("/cmd_lab3", data={"domain": "example.com", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"ok")
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_and_never_calls_popen(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("bad")
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com;rm -rf /", "os": "win"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"bad")
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
