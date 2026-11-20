import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _post(self, domain, os='win'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_invalid_domain_without_starting_process(self, popen):
        request = self._post('example.com; touch /tmp/injected')

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_passes_valid_domain_as_argument_without_shell(self, popen, render):
        popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self._post('www.example.com', os='win')

        cmd_lab3(request)

        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
