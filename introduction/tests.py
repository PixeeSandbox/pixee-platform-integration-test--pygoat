from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmd_lab_user",
            password="StrongPassword123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value.stdout = "lookup output"
        mock_run.return_value.stderr = ""

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )

        mock_run.assert_called_once_with(
            ["nslookup", "example.com"], capture_output=True, text=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup output")
