from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_semicolon_delimited_domain(self, mock_popen):
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; echo pwned", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_escaped_domain(self, mock_popen):
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "$(whoami).example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
