import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_without_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab3', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab3(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_domain_with_shell_metacharacter_is_rejected(self, popen):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; whoami',
            'os': 'linux',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        popen.assert_not_called()
        self.assertContains(response, 'Invalid domain')
