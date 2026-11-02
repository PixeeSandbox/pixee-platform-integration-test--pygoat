from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_run):
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; id", "os": "linux"},
        )

        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_accepts_valid_domain(self, mock_run):
        mock_process = Mock()
        mock_process.stdout = b"example output\n"
        mock_process.stderr = b""
        mock_run.return_value = mock_process

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com", "os": "win"},
        )

        self.assertContains(response, "example output")
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, check=True)
