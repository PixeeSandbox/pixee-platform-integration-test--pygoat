from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell_on_windows(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"stdout", b"stderr")

        response = self.client.post(
            self.url,
            {"domain": "https://www.example.com;whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com;whoami"])
        self.assertNotIn("shell", kwargs)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell_on_non_windows(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"stdout", b"stderr")

        response = self.client.post(
            self.url,
            {"domain": "https://www.example.com&&whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com&&whoami"])
        self.assertNotIn("shell", kwargs)
