from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_command_arguments(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"safe output", b"")
        mock_popen.return_value = mock_process

        self.client.force_login(self.user)
        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertIsInstance(args[0], list)
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        self.client.force_login(self.user)
        response = self.client.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
