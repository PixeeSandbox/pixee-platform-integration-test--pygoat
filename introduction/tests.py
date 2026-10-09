from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmdlab3user", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_executes_subprocess_with_argument_list(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"resolved", b"")

        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs["shell"])

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_invalid_domain_before_subprocess(self, mock_popen):
        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
