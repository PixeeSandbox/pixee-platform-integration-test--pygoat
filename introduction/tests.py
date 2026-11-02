import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password12345",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_posts_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"resolved\n", b"")
        mock_popen.return_value = process

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_posts_dig_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"dig output\n", b"")
        mock_popen.return_value = process

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.org", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dig output")
        mock_popen.assert_called_once_with(
            ["dig", "example.org"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
