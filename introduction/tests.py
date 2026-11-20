import subprocess
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = type("User", (), {"is_authenticated": True})()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_hostname_is_passed_as_a_separate_argument(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b"DNS output", b"")
        request = self.factory.post("/cmd_lab3", {"domain": "example.com", "os": "win"})
        request.user = self.user

        cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once()

    @patch("introduction.other_views.subprocess.Popen")
    def test_hostname_with_command_injection_syntax_is_rejected(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab3", {"domain": "example.com; whoami", "os": "win"}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
