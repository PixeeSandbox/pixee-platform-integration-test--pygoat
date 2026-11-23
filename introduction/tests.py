import subprocess
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import TestCase
from django.http import HttpResponseBadRequest

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def _post_request(self, domain, os="win"):
        return SimpleNamespace(
            user=SimpleNamespace(is_authenticated=True),
            method="POST",
            POST={"domain": domain, "os": os},
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_domain_with_shell_metacharacters_is_rejected(self, popen):
        response = cmd_lab3(self._post_request("example.com; whoami"))

        self.assertIsInstance(response, HttpResponseBadRequest)
        popen.assert_not_called()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_hostname_uses_dns_executable_without_shell(self, popen, render):
        process = Mock()
        process.communicate.return_value = (b"", b"")
        popen.return_value = process

        cmd_lab3(self._post_request("https://www.example.com", os="win"))

        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
