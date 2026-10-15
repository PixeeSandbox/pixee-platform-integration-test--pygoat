from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="testuser", password="testpass123")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        with patch("introduction.views.subprocess.run") as mock_run:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com; whoami", "os": "linux"},
            )

        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()
