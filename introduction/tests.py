from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password123",
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_executing_subprocess(self, mock_popen):
        self.client.force_login(self.user)
        response = self.client.post(
            "/cmd_lab3",
            {
                "domain": "example.com; cat /etc/passwd",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
