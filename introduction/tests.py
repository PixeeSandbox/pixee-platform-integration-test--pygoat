import subprocess
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"stdout", b"stderr")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"stdoutstderr", response.content)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com;id", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Something went wrong", response.content)
        mock_popen.assert_not_called()
