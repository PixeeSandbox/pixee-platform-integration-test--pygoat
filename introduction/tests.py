import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _post_request(self, domain, os='win'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, mock_popen, mock_render):
        cmd_lab3(self._post_request('example.com; touch /tmp/pwned'))

        mock_popen.assert_not_called()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_runs_dns_utility_with_separate_arguments(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b'output', b'')

        cmd_lab3(self._post_request('example.com'))

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
