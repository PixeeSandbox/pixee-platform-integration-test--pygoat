from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="cmduser", password="password123")
        self.client.login(username="cmduser", password="password123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"ok", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "example.com; rm -rf /",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com; rm -rf /"])
        self.assertNotIn("shell", kwargs)
