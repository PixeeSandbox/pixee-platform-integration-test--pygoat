from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_safe_hostname(self, mock_run):
        mock_run.return_value.stdout = "lookup ok\n"
        mock_run.return_value.stderr = ""

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )

        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lab/CMD/cmd_lab.html")
        self.assertContains(response, "lookup ok")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_shell_metacharacters_before_subprocess(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lab/CMD/cmd_lab.html")
        self.assertContains(response, "Something went wrong")
