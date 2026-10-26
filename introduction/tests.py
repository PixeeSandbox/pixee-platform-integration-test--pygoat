from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="Password123!")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"valid output", b"")
        mock_popen.return_value = process

        response = self.client.post("/cmd_lab3", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs.get("shell", False))
        self.assertIn("valid output", response.content.decode())

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "-example.com; rm -rf /", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn("Something went wrong", response.content.decode())
