from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import ANY, Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password123",
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_without_shell_for_safe_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "https://www.example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertContains(response, "lookup output")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
