import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_accepts_benign_hostname_and_uses_structured_subprocess_args(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("lookup ok", response.content.decode())
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters_before_subprocess(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; rm -rf /", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode())
        mock_popen.assert_not_called()
