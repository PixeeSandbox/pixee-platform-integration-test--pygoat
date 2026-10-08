from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post("/cmd_lab3", {"domain": "example.com;whoami", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_allows_valid_domain(self, mock_run):
        mock_run.return_value.stdout = "resolver output\n"
        mock_run.return_value.stderr = ""

        response = self.client.post("/cmd_lab3", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolver output")
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
