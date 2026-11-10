from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3SecurityTest(TestCase):
    def test_rejects_domain_with_shell_metacharacters(self):
        user = User.objects.create_user(username="cmd-test", password="password")
        self.client.force_login(user)

        with patch("introduction.other_views.subprocess.Popen") as popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; touch /tmp/payload", "os": "win"},
            )

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
