from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess


class CmdLabTests(TestCase):
    def test_cmd_lab_uses_shell_free_subprocess_arguments(self):
        User = get_user_model()
        user = User.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"lookup output", b"")

            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com; id", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com; id"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
