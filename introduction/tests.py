from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain_without_running_command(self):
        with patch("introduction.views.subprocess.run") as mock_run:
            response = self.client.post(
                "/cmd_lab",
                {
                    "domain": "example.com; rm -rf /",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()

    def test_cmd_lab_uses_safe_subprocess_arguments_for_valid_domain(self):
        mock_process = Mock(stdout="safe output\n", stderr="")
        with patch("introduction.views.subprocess.run", return_value=mock_process) as mock_run:
            response = self.client.post(
                "/cmd_lab",
                {
                    "domain": "example.com",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "safe output")
        mock_run.assert_called_once_with(["dig", "example.com"], capture_output=True, text=True)
