import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(user)

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_command_injection(self, popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; id", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Invalid hostname")
        popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_valid_hostname_uses_fixed_executable_and_separate_arguments(self, popen):
        popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
