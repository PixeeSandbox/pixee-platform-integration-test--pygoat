import subprocess
from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3TestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmd_lab_user",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup stdout", b"lookup stderr")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup stdoutlookup stderr")
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_injected_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com;whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
