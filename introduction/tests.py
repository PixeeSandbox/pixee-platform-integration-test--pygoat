import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cmdlab-user",
            password="StrongPassword123!",
        )

    def test_cmd_lab_rejects_malicious_domain_without_shell_execution(self):
        self.client.force_login(self.user)
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com;whoami", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_malicious_domain_input(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"dig output", b"")
        self.client.force_login(self.user)
        with patch("introduction.views.ipaddress.ip_address", side_effect=ValueError), patch(
            "introduction.views.re.fullmatch", return_value=object()
        ):
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com;whoami", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com;whoami"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertContains(response, "dig output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_nslookup_argument_list_for_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"windows dns output", b"")
        self.client.force_login(self.user)
        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertContains(response, "windows dns output")
