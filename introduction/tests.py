from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="cmdlabuser", password="password123")
        self.client.login(username="cmdlabuser", password="password123")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_safe_command_arguments(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"safe output", b"")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=ANY,
            stderr=ANY,
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malformed_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
