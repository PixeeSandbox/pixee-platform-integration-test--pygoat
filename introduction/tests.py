from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="password123")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com;id", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid domain", response.content)
        mock_run.assert_not_called()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value.stdout = "stdout\n"
        mock_run.return_value.stderr = ""
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertIn(b"stdout", response.content)
