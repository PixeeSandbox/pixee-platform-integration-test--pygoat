from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="cmdlabuser",
            email="cmdlabuser@example.com",
            password="testpass123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_windows_branch(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"windows output", b"")

        response = self.client.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_non_windows_branch(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"linux output", b"")
        malicious_domain = "example.com; rm -rf /"

        response = self.client.post(
            "/cmd_lab",
            data={"domain": malicious_domain, "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", malicious_domain],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
