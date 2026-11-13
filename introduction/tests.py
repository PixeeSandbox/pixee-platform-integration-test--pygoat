import subprocess
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_injection_shaped_domain_without_launching_subprocess(self, popen):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; whoami',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_invokes_dns_utility_with_validated_domain_and_no_shell(self, popen):
        process = Mock()
        process.communicate.return_value = (b'answer', b'')
        popen.return_value = process
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab3(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
