from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlab-user",
            password="test-password-123",
        )

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_safe_subprocess_arguments(self, mock_run):
        mock_run.return_value = Mock(stdout="resolved output", stderr="")
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertContains(response, "resolved output")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_invalid_domain_without_invoking_subprocess(self, mock_run):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")
