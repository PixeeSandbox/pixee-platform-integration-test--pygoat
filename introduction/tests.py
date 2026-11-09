from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="testpass123",
        )
        self.url = reverse("Command Injection Lab 3")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"domain": "example.com;id", "os": "win"},
        )

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_without_shell_for_valid_domain(self, mock_popen):
        self.client.force_login(self.user)
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup-ok", b"")

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "win"},
        )

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup-ok")
