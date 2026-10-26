import subprocess
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="StrongPass123!",
        )
        self.url = reverse("Command Injection Lab 3")

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        self.client.force_login(self.user)
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                self.url,
                {"domain": "example.com; rm -rf /", "os": "win"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_with_shell_disabled(self):
        self.client.force_login(self.user)
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"lookup output", b"")
        with patch("introduction.other_views.subprocess.Popen", return_value=process_mock) as mock_popen:
            response = self.client.post(
                self.url,
                {"domain": "example.com", "os": "win"},
            )
        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertIs(kwargs["shell"], False)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertContains(response, "lookup output")
