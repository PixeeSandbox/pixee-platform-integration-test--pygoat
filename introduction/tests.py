import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_on_non_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"answer", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; echo pwned", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com; echo pwned"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_on_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"answer", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com&&dir", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com&&dir"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
