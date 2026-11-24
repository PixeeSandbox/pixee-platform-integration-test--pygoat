import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _authenticated_post(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_syntax_without_subprocess(self, mock_popen):
        response = cmd_lab3(self._authenticated_post('example.com; whoami'))

        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid domain')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = cmd_lab3(self._authenticated_post('https://www.example.com', os='win'))

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'lookup output')
