from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmdtester", password="password123")
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            self.url,
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"ok", b"")

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertContains(response, "ok")
