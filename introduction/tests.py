import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="cmduser",
            email="cmduser@example.com",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_non_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"dig output", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"nslookup output", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
