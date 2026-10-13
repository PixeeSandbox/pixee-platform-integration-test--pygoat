from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmdtester", password="Password123!")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post("/cmd_lab3", {"domain": "example.com;rm -rf /", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_run.called)
        self.assertEqual(response.context[-1]["output"], "Something went wrong")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = Mock(stdout="example.com has address 93.184.216.34\n", stderr="", returncode=0)

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertEqual(response.context[-1]["output"], "example.com has address 93.184.216.34\n")
