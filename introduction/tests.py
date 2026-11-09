import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_malicious_domain_without_calling_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {
                "domain": "https://www.example.com; rm -rf /",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_safe_argument_list(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"resolved\n", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab3",
            {
                "domain": "https://www.example.com",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "resolved")
