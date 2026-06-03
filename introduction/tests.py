from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="StrongPassword123!"
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_windows_branch(self, mock_run):
        mock_run.return_value.stdout = "nslookup output\n"
        mock_run.return_value.stderr = ""

        response = self.client.post("/cmd_lab", {"domain": "https://www.example.com.", "os": "win"})

        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
            shell=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nslookup output")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_non_windows_branch(self, mock_run):
        mock_run.return_value.stdout = "dig output\n"
        mock_run.return_value.stderr = ""

        response = self.client.post("/cmd_lab", {"domain": "example.org", "os": "linux"})

        mock_run.assert_called_once_with(
            ["dig", "example.org"],
            capture_output=True,
            text=True,
            shell=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dig output")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess_call(self, mock_run):
        response = self.client.post("/cmd_lab", {"domain": "example.com;whoami", "os": "linux"})

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
