import subprocess

from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self):
        user = User.objects.create_user(username="tester", password="password123")
        self.client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post("/cmd_lab", {"domain": "example.com; id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argv_list_for_valid_domain(self):
        user = User.objects.create_user(username="tester2", password="password123")
        self.client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"example output", b"")
            response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "example output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
