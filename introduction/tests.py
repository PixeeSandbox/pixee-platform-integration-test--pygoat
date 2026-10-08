import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="cmduser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.run")
    def test_benign_hostname_uses_argument_vector_without_shell(self, mock_run):
        mock_run.return_value.stdout = "server: 8.8.8.8\n"
        mock_run.return_value.stderr = ""

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertContains(response, "server: 8.8.8.8")

    @patch("introduction.views.subprocess.run")
    def test_shell_metacharacters_are_rejected_without_invoking_subprocess(self, mock_run):
        response = self.client.post(
            self.url,
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Invalid domain")
