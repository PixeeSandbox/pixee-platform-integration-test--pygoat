import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdtester",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_list_arguments_for_allowed_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"resolved", b"")

        for os_value, expected_command in (("linux", ["dig", "example.com"]), ("win", ["nslookup", "example.com"])):
            mock_popen.reset_mock()
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com", "os": os_value},
            )

            self.assertEqual(response.status_code, 200)
            mock_popen.assert_called_once()
            called_args, called_kwargs = mock_popen.call_args
            self.assertEqual(called_args[0], expected_command)
            self.assertFalse(called_kwargs["shell"])
            self.assertEqual(called_kwargs["stdout"], subprocess.PIPE)
            self.assertEqual(called_kwargs["stderr"], subprocess.PIPE)
