from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="tester",
            password="secret123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_posts_valid_domain_without_shell(self, mock_run):
        mock_run.return_value = Mock(stdout="lookup ok", stderr="")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(response.context["output"], "lookup ok")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertEqual(response.context["output"], "Something went wrong")
