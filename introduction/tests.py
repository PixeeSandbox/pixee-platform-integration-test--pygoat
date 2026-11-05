from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_windows_branch(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"windows output", b"")

        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "https://www.example.com; whoami",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com; whoami"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_non_windows_branch(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"linux output", b"")

        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "https://www.example.org && id",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.org && id"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
