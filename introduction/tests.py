from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_non_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"dig-output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com;whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dig-output")
        mock_popen.assert_called_once_with(
            ["dig", "example.com;whoami"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"nslookup-output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com&&dir", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nslookup-output")
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com&&dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
