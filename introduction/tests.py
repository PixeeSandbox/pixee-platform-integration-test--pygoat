import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password123",
        )
        self.url = reverse("Command Injection Lab 3")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_windows_branch(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process

        response = self.client.post(self.url, {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_non_windows_branch(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process

        response = self.client.post(self.url, {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            self.url,
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
