import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_shell_metacharacters_in_domain(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "win"})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_passes_valid_domain_as_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

        self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
