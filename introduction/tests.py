from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="strong-password",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
