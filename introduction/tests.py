import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password12345",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_post_uses_argument_list_without_shell(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"dns output", b"")
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

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_popen(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
