from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CommandInjectionViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="command-test", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_command_injection_payload_rejected(self, mock_popen):
        response = self.client.post("/cmd_lab3", {
            "domain": "example.com; whoami",
            "os": "linux",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain name")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_passed_as_separate_process_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup result", b"")

        response = self.client.post("/cmd_lab3", {
            "domain": "https://www.example.com",
            "os": "win",
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
