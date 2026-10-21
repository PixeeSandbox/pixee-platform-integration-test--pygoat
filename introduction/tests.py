from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        User.objects.create_user(username="testuser", password="testpass123")
        self.assertTrue(self.client.login(username="testuser", password="testpass123"))

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"resolved\n", b"")
        mock_popen.return_value = process_mock

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertContains(response, "resolved")
