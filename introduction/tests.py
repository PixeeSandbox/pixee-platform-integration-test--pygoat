from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_uses_argv_without_shell_for_valid_domain(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"resolved", b"")

            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs["shell"])

    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com; rm -rf /", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
