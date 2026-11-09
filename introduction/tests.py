from unittest.mock import Mock, patch

import subprocess

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="testpassword123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_popen(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "example.com; rm -rf /",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_and_shell_false_for_valid_domain(self, mock_popen):
        mock_process = Mock()
        mock_process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = mock_process

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
