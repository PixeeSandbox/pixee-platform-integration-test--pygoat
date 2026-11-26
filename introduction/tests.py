from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def test_rejects_shell_metacharacters_without_running_command(self):
        user = User.objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(user)

        with patch("introduction.other_views.subprocess.Popen") as popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; echo injected", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        popen.assert_not_called()
