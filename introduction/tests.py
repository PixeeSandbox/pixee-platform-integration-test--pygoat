import subprocess
from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_linux(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"linux output", b"")

        domain = "example.com; whoami"
        response = self.client.post(
            "/cmd_lab",
            data={"domain": domain, "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", domain])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_windows(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"windows output", b"")

        domain = "example.com && whoami"
        response = self.client.post(
            "/cmd_lab",
            data={"domain": domain, "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", domain])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
