import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


User = get_user_model()


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        mock_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_and_shell_false(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"ok", b"")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
