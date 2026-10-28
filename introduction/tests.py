import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_nslookup_argv_for_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"windows output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertIs(kwargs["stdout"], subprocess.PIPE)
        self.assertIs(kwargs["stderr"], subprocess.PIPE)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "windows output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_dig_argv_for_non_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"linux output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertIs(kwargs["stdout"], subprocess.PIPE)
        self.assertIs(kwargs["stderr"], subprocess.PIPE)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "linux output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
