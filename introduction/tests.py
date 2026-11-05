from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="security_user", password="StrongPass123!")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_and_uses_argument_list(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"safe output", b"")

        malicious_response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com;whoami", "os": "win"},
        )
        self.assertContains(malicious_response, "Something went wrong")
        mock_popen.assert_not_called()

        mock_popen.reset_mock()

        safe_response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )
        self.assertEqual(safe_response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
