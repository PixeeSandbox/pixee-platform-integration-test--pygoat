import subprocess
from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def test_cmd_lab_uses_argv_list_without_shell(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(user)

        malicious_domain = "example.com; whoami && echo hacked"

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"lookup output", b"")

            response = self.client.post(
                "/cmd_lab",
                {"domain": malicious_domain, "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", malicious_domain])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
