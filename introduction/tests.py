import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Mock(is_authenticated=True)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"windows output", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_non_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"linux output", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "https://www.example.org", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.org"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
