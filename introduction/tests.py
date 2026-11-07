import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_posts_safe_domain_uses_argument_list(self, mock_run):
        mock_run.return_value = Mock(stdout="lookup ok", stderr="")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lab/CMD/cmd_lab.html")
        self.assertEqual(response.context["output"], "lookup ok")
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        response = self.client.post("/cmd_lab", {"domain": "--help", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lab/CMD/cmd_lab.html")
        self.assertEqual(response.context["output"], "Something went wrong")
        mock_run.assert_not_called()
