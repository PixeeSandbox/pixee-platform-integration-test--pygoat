from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def test_rejects_shell_metacharacters_without_running_subprocess(self):
        user = User.objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(user)

        with patch("introduction.other_views.subprocess.Popen") as process:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; touch /tmp/injected", "os": "linux"},
            )

        self.assertEqual(response.status_code, 400)
        process.assert_not_called()
