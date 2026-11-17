from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_malicious_domain_without_running_command(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; touch /tmp/pwned", "os": "linux"},
        )

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_runs_lookup_with_executable_and_domain_as_separate_arguments(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
