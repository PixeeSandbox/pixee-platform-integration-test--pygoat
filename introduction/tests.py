from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword123",
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_list_and_disables_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"resolved\n", b"")
        self.client.force_login(self.user)

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs["shell"])

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
