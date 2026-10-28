from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch

import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="Password123!")
        self.client.login(username="cmduser", password="Password123!")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_hostname_uses_structured_command(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_popen.called)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_hostname_before_subprocess(self, mock_popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com;id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertContains(response, "Something went wrong")
