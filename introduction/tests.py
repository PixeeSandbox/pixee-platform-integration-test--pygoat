import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


User = get_user_model()


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.username = "cmduser"
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(self.client.login(username=self.username, password=self.password))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_and_shell_false(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"answer", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_calling_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
