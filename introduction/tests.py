from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="testpass123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_and_disables_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_treats_metacharacters_as_literal_domain_argument(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        malicious_domain = "https://www.example.com;rm -rf /"
        response = self.client.post(
            "/cmd_lab",
            {"domain": malicious_domain, "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com;rm -rf /"])
        self.assertFalse(kwargs.get("shell", False))
