from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="testuser", password="testpass")
        self.client.force_login(user)

    @patch("introduction.views.subprocess.Popen")
    def test_valid_hostname_uses_argument_list_and_windows_lookup(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "  https://www.example.com  ", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertIs(kwargs["shell"], False)
        self.assertIn("lookup output", response.content.decode())

    @patch("introduction.views.subprocess.Popen")
    def test_invalid_hostname_is_rejected_before_process_execution(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; touch /tmp/injected", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid hostname")
        mock_popen.assert_not_called()
