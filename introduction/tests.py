import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlab-user",
            password="password123",
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"valid output", b"")
        self.client.force_login(self.user)

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "valid output")
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
