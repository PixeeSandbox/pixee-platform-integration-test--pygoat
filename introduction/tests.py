from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com;id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_invokes_process_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
