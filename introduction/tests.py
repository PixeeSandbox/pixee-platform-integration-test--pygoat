import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CommandInjectionLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_domain_with_shell_syntax(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; id", "os": "win"})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_fixed_executable_and_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup result", b"")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup result")
