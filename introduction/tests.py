from django.test import TestCase
from unittest.mock import Mock, patch

import subprocess

from django.contrib.auth import get_user_model


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com;whoami", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self):
        mock_process = Mock()
        mock_process.communicate.return_value = (b"lookup ok", b"")

        with patch("introduction.other_views.subprocess.Popen", return_value=mock_process) as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
