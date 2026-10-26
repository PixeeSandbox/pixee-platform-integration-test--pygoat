from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="cmdtester", password="StrongPass123!")
        self.client.force_login(self.user)

    @mock.patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_windows_branch_uses_argv_list(self, mock_popen):
        process = mock.Mock()
        process.communicate.return_value = (b"safe output", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "safe output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)

    @mock.patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_non_windows_branch_uses_argv_list(self, mock_popen):
        process = mock.Mock()
        process.communicate.return_value = (b"dig output", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.Example.org.", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "dig output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.org"])
        self.assertNotIn("shell", kwargs)

    @mock.patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_command(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
        mock_popen.assert_not_called()
