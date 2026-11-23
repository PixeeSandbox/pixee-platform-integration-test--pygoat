import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_rejects_shell_syntax_without_launching_subprocess(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = Mock(is_authenticated=True)

        with patch('introduction.other_views.render') as render, patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        popen.assert_not_called()
        render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'})
        self.assertEqual(response, render.return_value)

    def test_valid_hostname_passed_as_separate_dns_argument(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = Mock(is_authenticated=True)
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')

        with patch('introduction.other_views.render') as render, patch('introduction.other_views.subprocess.Popen', return_value=process) as popen:
            response = cmd_lab3(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'lookup output'})
        self.assertEqual(response, render.return_value)
