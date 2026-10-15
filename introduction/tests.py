from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_accepts_valid_hostname(self, mock_run):
        mock_run.return_value = Mock(stdout="lookup ok\n", stderr="")
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
