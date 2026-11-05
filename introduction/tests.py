from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters_in_domain(self):
        user = User.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as mocked_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com; cat /etc/passwd", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mocked_popen.assert_not_called()
