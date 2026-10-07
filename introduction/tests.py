from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3ValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com;whoami", "os": "win"},
            )

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Invalid input", status_code=400)
        mock_popen.assert_not_called()
