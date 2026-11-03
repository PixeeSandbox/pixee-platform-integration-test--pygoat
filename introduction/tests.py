from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_valid_domain_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs.get("shell", False))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"lookup output", response.content)

    @patch("introduction.views.subprocess.Popen")
    def test_malicious_domain_is_rejected_before_execution(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid domain", response.content)
