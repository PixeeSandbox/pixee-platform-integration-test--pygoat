from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmduser", password="pass12345")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argv_and_shell_false_for_valid_domain(self, mock_run):
        mock_run.return_value = SimpleNamespace(stdout="resolved\n", stderr="")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertContains(response, "resolved")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_shell_metacharacters_before_subprocess(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Invalid domain")
