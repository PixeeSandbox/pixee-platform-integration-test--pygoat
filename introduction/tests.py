from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="password123",
        )

    def test_cmd_lab3_uses_argument_list_for_valid_domain(self):
        with patch("introduction.other_views.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "resolved"
            mock_run.return_value.stderr = ""
            request = self.factory.post(
                "/cmd_lab3",
                {"domain": "example.com", "os": "linux"},
            )
            request.user = self.user

            response = other_views.cmd_lab3(request)

        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"resolved", response.content)

    def test_cmd_lab3_rejects_malicious_domain_without_calling_subprocess(self):
        with patch("introduction.other_views.subprocess.run") as mock_run:
            request = self.factory.post(
                "/cmd_lab3",
                {"domain": "example.com;id", "os": "linux"},
            )
            request.user = self.user

            response = other_views.cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Something went wrong", response.content)
