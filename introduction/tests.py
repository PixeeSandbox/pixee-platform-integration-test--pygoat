from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmdlab3user", password="testpass123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, popen_mock):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, popen_mock):
        process_mock = popen_mock.return_value
        process_mock.communicate.return_value = (b"lookup ok\n", b"")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once()
        self.assertEqual(popen_mock.call_args.args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", popen_mock.call_args.kwargs)

