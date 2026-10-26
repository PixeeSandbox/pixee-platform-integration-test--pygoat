from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_safe_argument_list(self, mock_run):
        mock_run.return_value = SimpleNamespace(stdout="example output\n", stderr="")
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertContains(response, "example output")
