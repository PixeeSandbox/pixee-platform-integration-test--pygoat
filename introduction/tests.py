import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmd-user",
            password="password123",
        )
        self.client.force_login(self.user)
        self.url = "/cmd_lab"

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            self.url,
            {"domain": "example.com; cat /etc/passwd", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_accepts_valid_ip_address(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["dig", "8.8.8.8"],
            returncode=0,
            stdout="8.8.8.8\n",
            stderr="",
        )

        response = self.client.post(
            self.url,
            {"domain": "8.8.8.8", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["dig", "8.8.8.8"],
            capture_output=True,
            text=True,
        )
        self.assertContains(response, "8.8.8.8")
