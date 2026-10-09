from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="cmdlabuser", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_injection_in_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
