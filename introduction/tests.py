from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_executes_safe_command(self, mock_run):
        mock_run.return_value = Mock(stdout="mocked stdout", stderr="mocked stderr")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        mock_run.assert_called_once_with(["dig", "example.com"], stdout=-1, stderr=-1, text=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "mocked stdoutmocked stderr")
