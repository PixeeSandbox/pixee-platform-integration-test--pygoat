from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch
import subprocess

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="tester",
            password="password123",
        )

    def test_cmd_lab_rejects_malicious_domain_without_running_command(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com;whoami", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab_runs_safe_command_with_argument_list(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )
        request.user = self.user
        process = Mock()
        process.communicate.return_value = (b"command output\n", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as mock_popen:
            response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "command output")
