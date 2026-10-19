import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="Password123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_list_for_benign_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"example.com\n", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertEqual(kwargs, {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE})

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_running_command(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
