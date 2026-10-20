from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.url = "/cmd_lab3"

    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self):
        self.client.force_login(self.user)
        with patch("introduction.other_views.subprocess.run") as mock_run:
            response = self.client.post(self.url, {"domain": "example.com; id", "os": "win"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_fixed_argv_without_shell(self, mock_run):
        self.client.force_login(self.user)
        mock_run.return_value = type("Result", (), {"stdout": "ok", "stderr": ""})()
        response = self.client.post(self.url, {"domain": "example.com", "os": "win"})
        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertFalse(mock_run.call_args.kwargs.get("shell", False))
        self.assertContains(response, "ok")
