import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _authenticated_post(self, data):
        request = self.factory.post('/cmd_lab3', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_injection_domain(self, popen):
        request = self._authenticated_post({
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_argument_list_for_valid_hostname(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self._authenticated_post({'domain': 'example.com', 'os': 'win'})

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
