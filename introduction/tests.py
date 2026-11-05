from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username="alice", password="testpass123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_executes_safe_domain_without_shell(self, mock_run):
        mock_run.return_value = Mock(stdout="resolved", stderr="")

        response = self.client.post("/cmd_lab", {"domain": "https://www.example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "resolved")
        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
        mock_run.assert_not_called()
