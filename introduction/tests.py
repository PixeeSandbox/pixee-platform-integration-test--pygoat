from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="StrongPass123!",
        )

    def login(self):
        self.assertTrue(
            self.client.login(username="cmduser", password="StrongPass123!")
        )

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_without_calling_subprocess(self, mock_run):
        self.login()

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Invalid input")
        mock_run.assert_not_called()

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_non_shell_argument_list_for_valid_domain(self, mock_run):
        self.login()
        mock_run.return_value = Mock(stdout="resolved\n", stderr="")

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertContains(response, "resolved")
