from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )
        self.client = Client()
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs.get("shell", False))
        self.assertContains(response, "lookup ok")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
