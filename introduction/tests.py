from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch, Mock


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "linux"})
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_allows_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"valid output", b"")
        mock_popen.return_value = process

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "valid output")
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ["dig", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
