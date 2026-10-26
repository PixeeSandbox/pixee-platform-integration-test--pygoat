import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_does_not_execute_injected_shell_content(self):
        User = get_user_model()
        user = User.objects.create_user(username="cmduser", password="password123")
        client = Client()
        client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"safe output", b"")

            response = client.post(
                "/cmd_lab",
                {"domain": "example.com; echo INJECTED", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("INJECTED", response.content.decode())
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com; echo INJECTED"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
