from types import SimpleNamespace
from unittest.mock import patch

import subprocess

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_hostname_with_shell_metacharacters_is_rejected(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab(request)

        mock_popen.assert_not_called()
