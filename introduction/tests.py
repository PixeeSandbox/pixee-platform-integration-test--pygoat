from types import SimpleNamespace
from unittest.mock import ANY, Mock, patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_windows_branch_uses_argument_list(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b"windows output", b"")
        popen_mock.return_value = process
        render_mock.return_value = Mock()

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com; id", "os": "win"},
        )
        request.user = self.user

        cmd_lab(request)

        popen_mock.assert_called_once_with(
            ["nslookup", "example.com; id"],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertFalse(popen_mock.call_args.kwargs.get("shell", False))

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_non_windows_branch_uses_argument_list(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b"linux output", b"")
        popen_mock.return_value = process
        render_mock.return_value = Mock()

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com && whoami", "os": "linux"},
        )
        request.user = self.user

        cmd_lab(request)

        popen_mock.assert_called_once_with(
            ["dig", "example.com && whoami"],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertFalse(popen_mock.call_args.kwargs.get("shell", False))
