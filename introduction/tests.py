from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_hostname(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid hostname")
        mock_popen.assert_not_called()
