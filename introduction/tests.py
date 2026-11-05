import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="testpass123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_windows_branch(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"win output", b"")

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com; whoami"])
        self.assertNotIn("shell", kwargs)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_non_windows_branch(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"dig output", b"")

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com && id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com && id"])
        self.assertNotIn("shell", kwargs)
