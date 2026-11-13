import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CommandLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_domain_uses_fixed_executable(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"DNS output", b"")

        response = self.client.post(reverse("Command Injection Lab"), {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post(reverse("Command Injection Lab"), {"domain": "example.com;whoami", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
