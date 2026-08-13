import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)

    def _mock_process(self):
        process = MagicMock()
        process.communicate.return_value = (b"resolved", b"")
        return process

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_accepts_safe_hostname(self, mock_popen):
        mock_popen.return_value = self._mock_process()
        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "linux"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injection_hostname(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;id", "os": "linux"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_accepts_safe_hostname(self, mock_popen):
        mock_popen.return_value = self._mock_process()
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_injection_hostname(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com&&whoami", "os": "win"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
