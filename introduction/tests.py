import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="test-user", password="test-password")
        self.client.force_login(user)

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_shell_metacharacters_without_running_subprocess(self, popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; touch /tmp/pwned", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b"DNS result", b"")

        response = self.client.post("/cmd_lab", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
