import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmdtester", password="testpass123")
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_metacharacters_and_uses_argument_list(self):
        with patch("introduction.other_views.subprocess.run") as run_mock:
            response = self.client.post("/cmd_lab3", {"domain": "example.com;id", "os": "win"})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Something went wrong")
            run_mock.assert_not_called()

        with patch("introduction.other_views.subprocess.run") as run_mock:
            run_mock.return_value = subprocess.CompletedProcess(
                args=["nslookup", "example.com"],
                returncode=0,
                stdout="example.com response",
                stderr="",
            )
            response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})
            self.assertEqual(response.status_code, 200)
            run_mock.assert_called_once_with(
                ["nslookup", "example.com"],
                shell=False,
                capture_output=True,
                text=True,
            )
            self.assertContains(response, "example.com response")
