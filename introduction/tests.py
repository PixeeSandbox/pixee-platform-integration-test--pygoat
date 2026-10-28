from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_shell_injection(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="tester", password="password123")
        self.client.force_login(user)

        process = Mock()
        process.communicate.return_value = (b"safe output", b"")

        with patch("introduction.other_views.subprocess.Popen", return_value=process) as popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; echo PWNED", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"PWNED", response.content)
        popen.assert_not_called()
