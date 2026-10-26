from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch("introduction.views.subprocess.Popen") as popen:
            response = self.client.post(
                "/cmd_lab",
                {
                    "domain": "https://www.example.com; whoami",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        popen.assert_not_called()

    def test_cmd_lab_processes_benign_hostname_without_shell(self):
        with patch("introduction.views.subprocess.Popen") as mock_process:
            mock_process.return_value.communicate.return_value = (b"lookup ok", b"")

            response = self.client.post(
                "/cmd_lab",
                {
                    "domain": "https://www.example.com",
                    "os": "win",
                },
            )

        mock_process.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
