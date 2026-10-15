from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="cmdlab3user", password="password123")
        self.client.force_login(user)

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        with patch("introduction.other_views.subprocess.run") as mock_run:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; whoami", "os": "linux"},
            )

        mock_run.assert_not_called()
        self.assertContains(response, "Invalid domain")
