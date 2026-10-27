from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CommandInjectionLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="password123")
        self.assertTrue(self.client.login(username="cmduser", password="password123"))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_without_shell_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args, (["nslookup", "example.com"],))
        self.assertFalse(kwargs.get("shell", False))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_popen(self, mock_popen):
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com;whoami", "os": "win"},
        )

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
