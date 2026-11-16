import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="password")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_shell_metacharacters_before_running_process(self, popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com;whoami", "os": "win"})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_invokes_process_with_validated_domain_arguments(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        self.client.post("/cmd_lab3", {"domain": "https://www.example.com", "os": "win"})

        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
