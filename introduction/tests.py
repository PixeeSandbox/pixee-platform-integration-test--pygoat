from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_rejects_malicious_domain_without_running_command(self, run_mock, render_mock):
        render_mock.return_value = HttpResponse("rendered")
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; whoami", "os": "win"},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b"rendered")
        run_mock.assert_not_called()
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2]["output"], "Invalid domain")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_valid_domain_uses_argument_list_and_renders_output(self, run_mock, render_mock):
        render_mock.return_value = HttpResponse("rendered")
        run_mock.return_value = Mock(stdout="lookup output\n", stderr="")
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b"rendered")
        run_mock.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2]["output"], "lookup output\n")
