import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.url = "/cmd_lab"

    def test_cmd_lab_rejects_malicious_domain(self):
        self.client.force_login(self.user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(self.url, {"domain": "example.com;id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_fixed_argument_list_for_valid_domain(self, mock_popen):
        self.client.force_login(self.user)
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"valid output", b"")

        response = self.client.post(self.url, {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "valid output")
