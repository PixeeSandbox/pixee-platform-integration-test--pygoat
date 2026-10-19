from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_subprocess_invocation_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"safe output", b"")
        mock_popen.return_value = process

        response = self.client.post("/cmd_lab", {"domain": "https://www.example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertContains(response, "safe output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
