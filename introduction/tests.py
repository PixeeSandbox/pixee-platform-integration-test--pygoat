from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import MagicMock, patch

import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_nslookup_without_shell_for_windows(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"output", b"")
        mock_popen.return_value = process

        domain = "example.com"
        response = self.client.post("/cmd_lab", {"domain": domain, "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_dig_without_shell_for_non_windows(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"output", b"")
        mock_popen.return_value = process

        domain = "example.org"
        response = self.client.post("/cmd_lab", {"domain": domain, "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
