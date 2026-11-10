from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_shell_metacharacters_without_starting_process(self, mock_popen):
        response = self.client.post(self.url, {"domain": "example.com;whoami", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_valid_domain_is_passed_as_argument_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post(self.url, {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.context["output"], "lookup output")
