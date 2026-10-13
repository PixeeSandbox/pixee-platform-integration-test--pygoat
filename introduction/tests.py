from types import SimpleNamespace
from unittest.mock import patch
import subprocess

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_and_shell_false_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
