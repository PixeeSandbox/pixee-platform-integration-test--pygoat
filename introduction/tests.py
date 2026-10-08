import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def test_cmd_lab3_valid_hostname_uses_safe_argv(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen, patch(
            "introduction.other_views.render"
        ) as mock_render:
            process = mock_popen.return_value
            process.communicate.return_value = (b"stdout", b"")
            mock_render.return_value = HttpResponse("ok")

            request = self.factory.post(
                "/cmd_lab3/",
                {"domain": "https://www.example.com", "os": "win"},
            )
            request.user = self.user

            response = cmd_lab3(request)

            mock_popen.assert_called_once_with(
                ["nslookup", "example.com"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"ok")

    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen, patch(
            "introduction.other_views.render"
        ) as mock_render:
            mock_render.return_value = HttpResponse("bad")

            request = self.factory.post(
                "/cmd_lab3/",
                {"domain": "example.com; rm -rf /", "os": "linux"},
            )
            request.user = self.user

            response = cmd_lab3(request)

            mock_popen.assert_not_called()
            self.assertEqual(mock_render.call_args[0][2]["output"], "Something went wrong")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"bad")
