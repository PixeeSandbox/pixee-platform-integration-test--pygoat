from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3ViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_argv_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"resolved\n", b"")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)

    @patch("introduction.other_views.subprocess.Popen")
    def test_malicious_domain_is_rejected_before_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertEqual(response.context["output"], "Something went wrong")
