import subprocess
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_win_uses_argument_list_and_disables_shell(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"win output", b"")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")

        domain = "example.com;rm -rf /"
        request = self.factory.post("/cmd_lab/", {"domain": domain, "os": "win"})
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", domain])
        self.assertEqual(args[0][1], domain)
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_non_win_uses_argument_list_and_disables_shell(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"non-win output", b"")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")

        domain = "example.org && whoami"
        request = self.factory.post("/cmd_lab/", {"domain": domain, "os": "linux"})
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", domain])
        self.assertEqual(args[0][1], domain)
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
