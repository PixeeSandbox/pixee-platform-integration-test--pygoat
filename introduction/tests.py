from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_shell_injection_payload(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_array_for_valid_host(self, mock_run):
        process = MagicMock()
        process.stdout = "ok\n"
        process.stderr = ""
        mock_run.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com/path", "os": "win"},
        )

        self.assertContains(response, "ok")
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertTrue(kwargs["text"])

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_allows_localhost(self, mock_run):
        process = MagicMock()
        process.stdout = "localhost ok\n"
        process.stderr = ""
        mock_run.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "localhost", "os": "linux"},
        )

        self.assertContains(response, "localhost ok")
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["dig", "localhost"])
        self.assertFalse(kwargs["shell"])
