from unittest.mock import patch

import subprocess

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="Password123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_for_non_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"dig output", b"")

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com; rm -rf /"])
        self.assertFalse(mock_popen.call_args.kwargs.get("shell"))
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_for_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"nslookup output", b"")

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com && calc", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com && calc"])
        self.assertFalse(mock_popen.call_args.kwargs.get("shell"))
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], subprocess.PIPE)
