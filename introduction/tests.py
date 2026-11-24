import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_lookup(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab3(request)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        self.post_lookup('example.com; whoami')

        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_passes_valid_domain_as_argument_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.post_lookup('example.com')

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
