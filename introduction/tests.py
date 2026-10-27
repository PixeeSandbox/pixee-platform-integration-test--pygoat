import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username="tester", password="password123")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_popen(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; whoami", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_with_shell_disabled_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"ok", b"")

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
