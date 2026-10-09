from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="password123",
        )
        self.client.force_login(self.user)
        self.url = "/cmd_lab3"

    def test_cmd_lab3_rejects_malicious_domain_without_shell_execution(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                self.url,
                {"domain": "example.com; whoami", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argv_list_for_valid_domain(self):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")

        with patch("introduction.other_views.subprocess.Popen", return_value=process) as mock_popen:
            response = self.client.post(
                self.url,
                {"domain": "example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
