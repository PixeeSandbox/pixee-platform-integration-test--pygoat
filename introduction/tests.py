from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.url = reverse("Command Injection Lab 3")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_benign_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"ok", b"")
        mock_popen.return_value = process

        self.client.force_login(self.user)
        response = self.client.post(self.url, {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"domain": "example.com; id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
