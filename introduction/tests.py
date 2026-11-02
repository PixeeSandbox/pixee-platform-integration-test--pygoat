import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.url = "/cmd_lab"

    def test_cmd_lab_rejects_malicious_domain(self):
        self.client.force_login(self.user)
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                self.url,
                {"domain": "example.com; rm -rf /", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_accepts_valid_domain(self, mock_popen):
        self.client.force_login(self.user)
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup ok")
