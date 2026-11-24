import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_fixed_executable_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        request = self.request_factory.post('/cmd_lab/', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = Mock(is_authenticated=True)

        cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_hostname_with_shell_metacharacters_is_rejected(self, mock_popen):
        request = self.request_factory.post('/cmd_lab/', {
            'domain': 'example.com; whoami',
            'os': 'win',
        })
        request.user = Mock(is_authenticated=True)

        cmd_lab(request)

        mock_popen.assert_not_called()
