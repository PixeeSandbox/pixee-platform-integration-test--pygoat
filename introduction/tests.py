from django.test import TestCase
from unittest.mock import ANY, Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_user(username="cmdlabuser", password="testpass123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_linux(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"linux stdout", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com; rm -rf /"],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"win stdout", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com; rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com; rm -rf /"],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
