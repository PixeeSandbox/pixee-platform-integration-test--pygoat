from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="strong-password123")
        self.assertTrue(self.client.login(username="testuser", password="strong-password123"))

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_run):
        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {"domain": "example.com; id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()
        self.assertNotIn(b"example.com; id", response.content)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = Mock(stdout="ok", stderr="")

        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertContains(response, "ok")
