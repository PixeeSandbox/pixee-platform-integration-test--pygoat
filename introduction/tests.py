import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_dns_lookup(self, mock_popen):
        self.client.force_login(self.user)
        process = mock_popen.return_value
        process.communicate.return_value = (b"resolved", b"")

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "resolved")
