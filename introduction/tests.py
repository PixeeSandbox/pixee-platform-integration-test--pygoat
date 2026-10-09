from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = SimpleNamespace(
            communicate=lambda: (b"stdout", b"stderr")
        )
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com; rm -rf /"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(kwargs["stdout"], views.subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], views.subprocess.PIPE)
