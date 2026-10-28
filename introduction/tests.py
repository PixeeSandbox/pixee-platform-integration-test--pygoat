import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_running_command(self, mock_popen):
        response = self.client.post(
            self.url,
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
