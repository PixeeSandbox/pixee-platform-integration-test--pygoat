from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch
from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User(username="tester")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_fixed_argv_for_valid_hostname(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup result", b"")
        request = self.factory.post("/cmd_lab/", {"domain": "https://www.example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
        mock_popen.return_value.communicate.assert_called_once_with()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup result")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_dig_for_valid_hostname(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup result", b"")
        request = self.factory.post("/cmd_lab/", {"domain": "example.com", "os": "linux"})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup result")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_syntax_and_missing_domain(self, mock_popen):
        for data in ({"domain": "example.com; whoami"}, {}):
            request = self.factory.post("/cmd_lab/", data)
            request.user = self.user

            response = cmd_lab(request)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
