import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_popen(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; touch /tmp/pwned", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab3_invokes_popen_with_argument_list_and_shell_disabled(self):
        process = Mock()
        process.communicate.return_value = (b"resolved", b"")

        with patch("introduction.other_views.subprocess.Popen", return_value=process) as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
