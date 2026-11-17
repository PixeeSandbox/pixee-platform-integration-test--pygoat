from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponseBadRequest
from django.test import RequestFactory, TestCase

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_request(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_hostname_with_shell_metacharacters(self, popen):
        response = other_views.cmd_lab3(self.post_request('example.com; id'))

        self.assertIsInstance(response, HttpResponseBadRequest)
        popen.assert_not_called()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_invokes_lookup_with_hostname_as_separate_argument(self, popen, render):
        popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.post_request('example.com', os='win')

        other_views.cmd_lab3(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
