from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_safe_argument_list_for_valid_hostname(self, mock_run):
        mock_run.return_value = Mock(stdout="resolved\n", stderr="")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertNotIn("shell", mock_run.call_args.kwargs)
        self.assertContains(response, "resolved")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Invalid domain")
