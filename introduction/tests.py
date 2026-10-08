from unittest.mock import Mock, patch

import subprocess

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabCommandInjectionRegressionTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="cmduser",
            password="safe-password",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        self.client.login(username="cmduser", password="safe-password")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        self.client.login(username="cmduser", password="safe-password")

        process = Mock()
        process.communicate.return_value = (b"resolved\n", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )

        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "resolved")
