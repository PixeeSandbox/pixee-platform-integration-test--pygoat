import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_domain_with_shell_metacharacters_is_rejected(self):
        request = self.factory.post('/cmd/', {'domain': 'example.com;id', 'os': 'win'})
        request.user = Mock(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen, \
                patch('introduction.other_views.render') as render:
            cmd_lab3(request)

        popen.assert_not_called()
        render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'})

    def test_valid_hostname_uses_fixed_dns_executable(self):
        request = self.factory.post('/cmd/', {'domain': 'example.com', 'os': 'win'})
        request.user = Mock(is_authenticated=True)
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as popen, \
                patch('introduction.other_views.render'):
            cmd_lab3(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
