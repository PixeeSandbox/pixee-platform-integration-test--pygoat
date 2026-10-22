import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="StrongPass123!",
        )
        self.url = "/cmd_lab3"

    def test_cmd_lab3_rejects_malicious_domain(self):
        self.client.force_login(self.user)

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                self.url,
                {"domain": "example.com;id", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_and_shell_false(self):
        self.client.force_login(self.user)

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"lookup ok", b"")
            response = self.client.post(
                self.url,
                {"domain": "example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
