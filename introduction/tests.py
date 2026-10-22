from unittest.mock import MagicMock, patch

import subprocess

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="StrongPass123!",
        )
        self.url = "/cmd_lab"

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        self.client.force_login(self.user)
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"example output", b"")
        mock_popen.return_value = process_mock

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertEqual(response.context["output"], "example output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertEqual(response.context["output"], "Invalid domain name")
