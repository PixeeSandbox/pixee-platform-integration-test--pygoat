from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_dig(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"dig output", b"")

        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "https://www.example.com; rm -rf /",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com; rm -rf /"])
        self.assertFalse(kwargs.get("shell", False))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_nslookup(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"nslookup output", b"")

        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "https://www.example.com; whoami",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com; whoami"])
        self.assertFalse(kwargs.get("shell", False))
