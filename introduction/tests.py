from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmdlab3user", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_valid_domain_proceeds_normally(self, mock_run):
        mock_run.return_value = SimpleNamespace(stdout="lookup ok", stderr="")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["dig", "example.com"], capture_output=True, text=True)
        self.assertContains(response, "lookup ok")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_malicious_domain_is_rejected(self, mock_run):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Invalid domain")
