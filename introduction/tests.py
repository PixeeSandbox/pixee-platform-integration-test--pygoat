from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

User = get_user_model()


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab 3")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post(self.url, {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_list_arguments(self, mock_run):
        mock_run.return_value.stdout = "resolved\n"
        mock_run.return_value.stderr = ""

        response = self.client.post(self.url, {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["dig", "example.com"], capture_output=True, text=True, check=False)
        self.assertContains(response, "resolved")
