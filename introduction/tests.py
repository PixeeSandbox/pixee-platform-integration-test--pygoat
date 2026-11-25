from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_shell_metacharacters(self, popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com;whoami", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Invalid hostname")
        popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_uses_argument_list_for_valid_hostname(self, popen):
        popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_uses_dig_for_non_windows_hostname_lookup(self, popen):
        popen.return_value.communicate.return_value = (b"lookup output", b"")

        self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
