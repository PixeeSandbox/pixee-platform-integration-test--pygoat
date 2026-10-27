from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdtester",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)
        self.url = "/cmd_lab3"

    @patch("introduction.other_views.subprocess.run")
    def test_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post(
            self.url,
            {"domain": "example.com;id", "os": "win"},
        )

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Invalid domain")
        self.assertContains(response, "Invalid domain")

    @patch("introduction.other_views.subprocess.run")
    def test_uses_fixed_argv_for_valid_domain(self, mock_run):
        mock_run.return_value = MagicMock(stdout="lookup output", stderr="")

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "win"},
        )

        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "lookup output")
        self.assertContains(response, "lookup output")
