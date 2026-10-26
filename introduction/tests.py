from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3ValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tempuser",
            password="TempPass123!",
        )
        self.client.login(username="tempuser", password="TempPass123!")

    def test_cmd_lab3_rejects_malicious_domain(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {
                    "domain": "example.com;id",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
