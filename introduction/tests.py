import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="cmdlab3user",
            email="cmdlab3user@example.com",
            password="password123",
        )

    def test_rejects_malicious_domain_without_running_command(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = cmd_lab3(request)

        self.assertFalse(mock_popen.called)
        self.assertContains(response, "Invalid domain name")

    def test_uses_list_form_command_invocation_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            mock_popen.return_value.communicate.return_value = (b"example output", b"")
            response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "example output")
