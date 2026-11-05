import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="alice",
            password="S3curepass123",
        )
        self.assertTrue(
            self.client.login(username="alice", password="S3curepass123")
        )
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_execution(self, mock_popen):
        response = self.client.post(
            self.url,
            {"domain": "example.com; id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_nslookup_with_safe_argv_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"resolved", b"")

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_dig_with_safe_argv_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"resolved", b"")

        response = self.client.post(
            self.url,
            {"domain": "example.org", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.org"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
