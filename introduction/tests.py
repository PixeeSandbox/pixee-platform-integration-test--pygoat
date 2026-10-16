from unittest.mock import MagicMock, patch

import subprocess

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup ok")
