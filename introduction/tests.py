from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="TestPass123!",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain_without_executing_command(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com;id", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain supplied")
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_and_no_shell_for_valid_domain(self):
        process = patch("introduction.views.subprocess.Popen")
        with process as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"dns output", b"")

            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertContains(response, "dns output")
