from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.login(username="testuser", password="testpass123")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.-evil.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()
