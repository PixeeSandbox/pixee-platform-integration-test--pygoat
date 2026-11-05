from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.url = reverse("Command Injection Lab 3")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_calling_popen(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"domain": "https://www.example.com;whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_and_shell_disabled(self, mock_popen):
        self.client.force_login(self.user)
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        response = self.client.post(
            self.url,
            {"domain": "https://www.example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
        self.assertContains(response, "lookup ok")
