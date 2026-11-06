from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.url = "/cmd_lab3"

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"valid output", b"")
        self.assertTrue(self.client.login(username=self.user.username, password="testpass123"))

        response = self.client.post(self.url, {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertContains(response, "valid output")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen):
        self.assertTrue(self.client.login(username=self.user.username, password="testpass123"))

        response = self.client.post(self.url, {"domain": "example.com; id && whoami", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
