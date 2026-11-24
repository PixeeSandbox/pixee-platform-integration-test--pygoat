from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username="cmd-lab-user", password="password")
        self.client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as popen:
            response = self.client.post("/cmd_lab", {"domain": "example.com; touch /tmp/pwned", "os": "linux"})

        self.assertContains(response, "Invalid domain")
        popen.assert_not_called()
