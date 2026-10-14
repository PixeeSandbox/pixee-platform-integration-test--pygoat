import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab 3")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        response = self.client.post(
            self.url,
            {"domain": "example.com; id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"resolver output", b"")
        mock_popen.return_value = process

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell"))
        self.assertIs(kwargs.get("stdout"), subprocess.PIPE)
        self.assertIs(kwargs.get("stderr"), subprocess.PIPE)
        self.assertContains(response, "resolver output")
