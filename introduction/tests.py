import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="cmdlabuser",
            password="Password123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["nslookup", "example.com"],
            returncode=0,
            stdout="example.com response\n",
            stderr="",
        )

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lab/CMD/cmd_lab.html")
        self.assertEqual(response.context["output"], "example.com response\n")
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            capture_output=True,
            text=True,
        )

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lab/CMD/cmd_lab.html")
        self.assertEqual(response.context["output"], "Something went wrong")
        mock_run.assert_not_called()
