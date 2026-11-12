import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post(self, domain, os='win'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os})
        request.user = Mock(is_authenticated=True)
        return cmd_lab3(request)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain(self, popen):
        self.post('example.com; touch /tmp/injected')

        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_passed_as_argument_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.post('www.example.com')

        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    @patch('introduction.other_views.subprocess.Popen')
    def test_non_windows_uses_dig(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.post('www.example.com', os='linux')

        popen.assert_called_once_with(
            ['dig', 'www.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
