from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from unittest.mock import ANY, patch
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertEqual(response.context[0]["output"], "Something went wrong")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_with_shell_disabled(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"example output", b"")

        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertIn("example output", response.context[0]["output"])
