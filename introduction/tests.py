import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="securityuser", password="secret123")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain_without_popen(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com; rm -rf /", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_without_shell(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"safe output", b"")

            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertContains(response, "safe output")
