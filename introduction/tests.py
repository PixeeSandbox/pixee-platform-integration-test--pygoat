from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmdtester", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_windows_branch_uses_argument_list(self, mock_popen):
        mock_process = Mock()
        mock_process.communicate.return_value = (b"windows lookup\n", b"")
        mock_popen.return_value = mock_process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )

        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(response.context["output"], "windows lookup\n")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_non_windows_branch_uses_argument_list(self, mock_popen):
        mock_process = Mock()
        mock_process.communicate.return_value = (b"unix lookup\n", b"")
        mock_popen.return_value = mock_process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.org", "os": "linux"},
        )

        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.org"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(response.context["output"], "unix lookup\n")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_invoking_popen(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        mock_popen.assert_not_called()
        self.assertEqual(response.context["output"], "Invalid domain")
