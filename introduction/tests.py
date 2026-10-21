import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_without_running_subprocess(self, mock_run):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_runs_command_with_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = SimpleNamespace(stdout="example.com: 93.184.216.34\n", stderr="")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "example.com: 93.184.216.34")
