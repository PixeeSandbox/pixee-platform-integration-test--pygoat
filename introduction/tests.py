import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmd-user",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["dig", "example.com"],
            returncode=0,
            stdout="resolved\n",
            stderr="",
        )

        response = self.client.post(
            "/cmd_lab3",
            {"domain": " example.com ", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args.args[0], ["dig", "example.com"])
        self.assertNotIn("shell", mock_run.call_args.kwargs)
        self.assertContains(response, "resolved")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malformed_domain_before_execution(self, mock_run):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")
