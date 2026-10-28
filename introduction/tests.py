import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLabTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser",
            password="testpassword123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_non_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"safe output", b"")
        mock_popen.return_value = process

        malicious_domain = "example.com; cat /etc/passwd"
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": malicious_domain, "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", malicious_domain],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"safe output", b"")
        mock_popen.return_value = process

        malicious_domain = "example.com && whoami"
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": malicious_domain, "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", malicious_domain],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
