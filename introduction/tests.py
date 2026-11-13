import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmd-lab-user", password="password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_shell_metacharacters_without_running_command(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; touch /tmp/injected", "os": "win"},
        )

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_runs_lookup_with_separate_arguments_and_no_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"lookup error")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
