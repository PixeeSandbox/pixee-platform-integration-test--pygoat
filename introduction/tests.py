from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_request(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, popen, render):
        other_views.cmd_lab3(self.post_request('example.com; whoami'))

        popen.assert_not_called()
        render.assert_called_once()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_shell_free_argument_vector_for_valid_domain(self, popen, render):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        other_views.cmd_lab3(self.post_request('https://www.example.com', os='win'))

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
