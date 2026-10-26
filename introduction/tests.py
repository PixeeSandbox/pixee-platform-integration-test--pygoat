from unittest.mock import patch
import subprocess

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPassword123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_valid_hostname_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_malicious_payload_is_rejected_before_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
