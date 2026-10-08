import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="testpass123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_valid_domain_uses_safe_subprocess_args(self, mock_run):
        mock_run.return_value = Mock(stdout="example.com lookup\n", stderr="")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lab/CMD/cmd_lab.html")
        self.assertContains(response, "example.com lookup")
        self.assertEqual(mock_run.call_args.args[0], ["nslookup", "example.com"])
        self.assertEqual(mock_run.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(mock_run.call_args.kwargs["stderr"], subprocess.PIPE)
        self.assertTrue(mock_run.call_args.kwargs["text"])

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malformed_domain_without_running_command(self, mock_run):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; rm -rf /", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lab/CMD/cmd_lab.html")
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()
