import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="password")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_and_disables_shell(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"example output", b"")
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], subprocess.PIPE)
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
