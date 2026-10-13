from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_windows_branch(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"windows output", b"")

        payload = "example.com & whoami"
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": payload, "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", payload],
            stdout=-1,
            stderr=-1,
        )
        process.communicate.assert_called_once_with()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_non_windows_branch(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"linux output", b"")

        payload = "example.com; cat /etc/passwd"
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": payload, "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", payload],
            stdout=-1,
            stderr=-1,
        )
        process.communicate.assert_called_once_with()
