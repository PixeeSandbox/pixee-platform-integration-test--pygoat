import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="command-lab-user", password="password")
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab 3")

    @patch("introduction.other_views.subprocess.Popen")
    def test_benign_domain_uses_shell_free_lookup(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post(self.url, {"domain": "example.com", "os": "win"})

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup output")

    @patch("introduction.other_views.subprocess.Popen")
    def test_malicious_domain_is_rejected(self, mock_popen):
        response = self.client.post(
            self.url,
            {"domain": "example.com; touch /tmp/pwned", "os": "win"},
        )

        mock_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")
