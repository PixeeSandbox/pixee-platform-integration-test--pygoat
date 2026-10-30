from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password123",
        )
        self.url = "/cmd_lab"

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_benign_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"ok", b"")
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_hostname_without_invoking_popen(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"domain": "example.com; id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
