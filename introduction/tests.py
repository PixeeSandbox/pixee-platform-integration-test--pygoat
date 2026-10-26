from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_without_subprocess(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            data={"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argv_invocation_for_valid_domain(self, mock_run):
        mock_run.return_value = Mock(stdout="lookup ok", stderr="")

        response = self.client.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "win"},
        )

        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
