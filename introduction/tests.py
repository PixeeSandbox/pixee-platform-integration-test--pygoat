from unittest.mock import patch

import subprocess

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.username = "cmdlabuser"
        self.password = "StrongPass123!"
        User.objects.create_user(username=self.username, password=self.password)
        self.assertTrue(self.client.login(username=self.username, password=self.password))

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_list_without_shell(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"example output", b"")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_launching_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
