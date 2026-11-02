import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="StrongPass123!")
        self.assertTrue(self.client.login(username="cmduser", password="StrongPass123!"))

    @patch("introduction.other_views.subprocess.Popen")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Invalid domain provided")
        mock_run.assert_not_called()
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_non_shell_subprocess_for_valid_domain(self, mock_run):
        mock_run.return_value = Mock(stdout="lookup ok\n", stderr="")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )

        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "lookup ok\n")
