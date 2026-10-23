from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_win_branch_uses_argument_list(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"win-output", b"")
        mock_popen.return_value = process
        mock_render.return_value = MagicMock()

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com; rm -rf /"])
        self.assertFalse(kwargs.get("shell", False))

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_non_win_branch_uses_argument_list(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"dig-output", b"")
        mock_popen.return_value = process
        mock_render.return_value = MagicMock()

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com && calc", "os": "linux"},
        )
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com && calc"])
        self.assertFalse(kwargs.get("shell", False))
