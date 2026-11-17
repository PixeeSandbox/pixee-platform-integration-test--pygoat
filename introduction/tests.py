import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd(self, domain, os="linux"):
        request = self.factory.post("/cmd_lab3", {"domain": domain, "os": os})
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab3(request)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        response = self.post_cmd("example.com; whoami")

        popen.assert_not_called()
        self.assertIn(b"Invalid domain", response.content)

    @patch("introduction.other_views.subprocess.Popen")
    def test_invokes_lookup_safely_for_valid_hostname(self, popen):
        popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.post_cmd("www.example.com")

        popen.assert_called_once_with(
            ["dig", "www.example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIn(b"lookup output", response.content)
