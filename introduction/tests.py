from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_malicious_domain_without_calling_subprocess(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertFalse(mock_popen.called)
        self.assertContains(response, "Something went wrong")

    @patch("introduction.other_views.subprocess.Popen")
    def test_uses_argument_list_for_valid_domain(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"result", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=-1,
            stderr=-1,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertContains(response, "result")
