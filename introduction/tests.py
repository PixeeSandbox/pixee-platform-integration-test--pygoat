import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_valid_domain_uses_argv_and_shell_false(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b"lookup ok", b"")
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])
        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.content.decode(), "lookup ok")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_injected_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])
        request = self.factory.post("/cmd_lab", {"domain": "example.com;rm -rf /", "os": "linux"})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.content.decode(), "Invalid domain")
