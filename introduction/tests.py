import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_valid_hostname_is_passed_as_separate_argument(self, popen):
        popen.return_value.communicate.return_value = (b"lookup result", b"")

        self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_hostname_with_command_injection_syntax_is_rejected(self, popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
