import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="password")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_invokes_process_with_valid_hostname(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
