import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="testuser", password="password")
        self.client.force_login(user)
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_domain_with_shell_syntax(self, mock_popen):
        response = self.client.post(self.url, {"domain": "example.com; whoami"})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post(self.url, {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
