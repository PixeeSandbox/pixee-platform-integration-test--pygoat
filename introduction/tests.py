import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_safe_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"safe output", b"")
        mock_popen.return_value = process

        response = self.client.post("/cmd_lab", {
            "domain": "https://www.example.com",
            "os": "win",
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        process.communicate.assert_called_once()
        self.assertContains(response, "safe output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_popen(self, mock_popen):
        response = self.client.post("/cmd_lab", {
            "domain": "https://www.example.com && whoami",
            "os": "linux",
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
