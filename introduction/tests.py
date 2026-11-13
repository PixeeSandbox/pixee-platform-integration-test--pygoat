import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmdtest", password="password")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_shell_metacharacters_without_starting_process(self, popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com;id", "os": "win"})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_runs_lookup_with_validated_hostname_as_argument(self, popen):
        popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab3", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
