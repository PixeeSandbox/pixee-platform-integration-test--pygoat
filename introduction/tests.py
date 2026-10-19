import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmdlabuser", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["nslookup", "example.com"],
            returncode=0,
            stdout="lookup output",
            stderr="",
        )

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "lookup output")
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertTrue(kwargs["text"])
        self.assertFalse(kwargs["check"])

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; rm -rf /", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()
