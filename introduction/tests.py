import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_malicious_domain_without_calling_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "example.com; rm -rf /",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_and_shell_false(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"", b"")

        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "example.com",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
