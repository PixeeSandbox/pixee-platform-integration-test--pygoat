from unittest.mock import patch

import subprocess

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="secret")

    def test_cmd_lab_rejects_invalid_domain_without_invoking_subprocess(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com;rm -rf /", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_and_shell_false_for_windows(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "http://www.example.com", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            mock_popen.return_value.communicate.return_value = (b"lookup ok", b"")
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], subprocess.PIPE)

    def test_cmd_lab_uses_dig_for_non_windows(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            mock_popen.return_value.communicate.return_value = (b"lookup ok", b"")
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
