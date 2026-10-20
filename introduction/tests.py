from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="Passw0rd123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_run):
        mock_run.return_value.stdout = "lookup ok"
        mock_run.return_value.stderr = ""

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertContains(response, "lookup ok")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Invalid domain")
