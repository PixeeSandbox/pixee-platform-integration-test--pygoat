from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="testpass123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value.stdout = b"resolved output"
        mock_run.return_value.stderr = b""

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved output")
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell", False))

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain_without_running_subprocess(self, mock_run):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()
