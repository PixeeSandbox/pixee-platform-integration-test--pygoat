from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="StrongPass123!")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {
                "domain": "https://www.example.com; rm -rf /",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain provided")
        mock_popen.assert_not_called()
