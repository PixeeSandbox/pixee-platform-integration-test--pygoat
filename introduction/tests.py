from unittest.mock import patch

import subprocess
from django.test import RequestFactory, TestCase
from types import SimpleNamespace

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_hostname_with_shell_metacharacters(self, popen):
        request = self.factory.post('/cmd_lab/', {
            'domain': 'example.com; touch /tmp/pwned',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid hostname')
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')
        request = self.factory.post('/cmd_lab/', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
