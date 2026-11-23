import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_rejects_domain_with_shell_metacharacters(self):
        request = self.factory.post('/cmd-lab3/', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(popen.called)

    def test_passes_valid_hostname_as_separate_argument(self):
        request = self.factory.post('/cmd-lab3/', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)
        with patch('introduction.other_views.subprocess.Popen') as popen:
            popen.return_value.communicate.return_value = (b'lookup output', b'')
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
