import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.url = "/cmd_lab"

    def test_cmd_lab_rejects_malicious_domain_without_running_command(self):
        self.client.force_login(self.user)

        with patch("introduction.views.subprocess.run") as mock_run:
            response = self.client.post(
                self.url,
                {"domain": "example.com; whoami", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_safe_subprocess_invocation_for_valid_domain(self, mock_run):
        self.client.force_login(self.user)
        mock_run.return_value = subprocess.CompletedProcess(
            args=["nslookup", "example.com"],
            returncode=0,
            stdout="resolver output",
            stderr="",
        )

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            capture_output=True,
            text=True,
        )
        self.assertContains(response, "resolver output")
