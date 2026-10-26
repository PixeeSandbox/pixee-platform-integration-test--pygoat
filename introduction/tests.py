from unittest.mock import MagicMock, patch
import subprocess

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="pass12345")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_valid_post_uses_argument_list(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"result", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid domain", response.content)
        mock_popen.assert_not_called()
