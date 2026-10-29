from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_vector_for_safe_hostname(self, mock_run):
        mock_run.return_value = Mock(stdout="safe output", stderr="")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["dig", "example.com"], shell=False, capture_output=True, text=True
        )
        self.assertContains(response, "safe output")
