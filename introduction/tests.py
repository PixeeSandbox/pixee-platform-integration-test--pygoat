from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_lookup(self, domain, os="linux"):
        request = self.factory.post("/cmd/", {"domain": domain, "os": os})
        request.user = SimpleNamespace(is_authenticated=True)
        return other_views.cmd_lab3(request)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_shell_syntax_without_launching_subprocess(self, popen, render):
        self.post_lookup("example.com; whoami")

        popen.assert_not_called()
        render.assert_called_once()
        self.assertEqual(render.call_args[0][1:], (
            "Lab/CMD/cmd_lab.html",
            {"output": "Invalid domain"},
        ))

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_hostname_uses_fixed_executable_and_argument_list(self, popen, render):
        popen.return_value.communicate.return_value = (b"lookup output", b"")

        self.post_lookup("example.com", os="win")

        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
