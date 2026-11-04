import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username="cmduser", password="secure-password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_invalid_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
