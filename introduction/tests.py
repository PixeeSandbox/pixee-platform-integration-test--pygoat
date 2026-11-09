import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionRegressionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmd_user",
            password="test-password-123",
        )
        self.client.force_login(self.user)

    def test_cmd_labs_reject_shell_metacharacters(self):
        for url_name, patch_path, os_value in (
            ("Command Injection Lab", "introduction.views.subprocess.Popen", "win"),
            ("Command Injection Lab 3", "introduction.other_views.subprocess.Popen", "linux"),
        ):
            with self.subTest(url_name=url_name):
                with patch(patch_path) as mock_popen:
                    response = self.client.post(
                        reverse(url_name),
                        {"domain": "example.com;id", "os": os_value},
                    )
                self.assertContains(response, "Something went wrong")
                mock_popen.assert_not_called()

    def test_cmd_labs_allow_valid_hostnames_with_argument_lists(self):
        for url_name, patch_path, os_value, expected_command in (
            ("Command Injection Lab", "introduction.views.subprocess.Popen", "win", "nslookup"),
            ("Command Injection Lab 3", "introduction.other_views.subprocess.Popen", "linux", "dig"),
        ):
            with self.subTest(url_name=url_name):
                with patch(patch_path) as mock_popen:
                    mock_process = mock_popen.return_value
                    mock_process.communicate.return_value = (b"safe dns output", b"")
                    response = self.client.post(
                        reverse(url_name),
                        {"domain": "example.com", "os": os_value},
                    )
                self.assertContains(response, "safe dns output")
                mock_popen.assert_called_once_with(
                    [expected_command, "example.com"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
