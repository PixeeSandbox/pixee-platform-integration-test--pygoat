import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b"", b"")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
