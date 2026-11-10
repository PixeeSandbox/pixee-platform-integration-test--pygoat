from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionTests(TestCase):
    def test_rejects_shell_metacharacters_without_running_command(self):
        user = get_user_model().objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(user)

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "win"})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
