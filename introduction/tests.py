from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com;rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_allows_benign_hostname(self, mock_run):
        completed = MagicMock()
        completed.stdout = "ok\n"
        completed.stderr = "warn\n"
        mock_run.return_value = completed

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ok")
        self.assertContains(response, "warn")
        mock_run.assert_called_once_with(["dig", "example.com"], capture_output=True, text=True)
