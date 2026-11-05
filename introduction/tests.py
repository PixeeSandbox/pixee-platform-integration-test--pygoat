from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3RegressionTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="cmdlab3user",
            password="StrongPass123!",
        )
        self.assertTrue(
            self.client.login(username="cmdlab3user", password="StrongPass123!")
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {
                "domain": "example.com; cat /etc/passwd",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Invalid domain")
        mock_popen.assert_not_called()
