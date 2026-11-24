import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_valid_hostname_uses_separate_arguments_without_a_shell(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        response = object()

        with patch('introduction.other_views.subprocess.Popen') as popen, patch('introduction.other_views.render', return_value=response):
            popen.return_value.communicate.return_value = (b'lookup result', b'')
            result = cmd_lab3(request)

        self.assertIs(result, response)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_hostname_with_shell_metacharacters_is_rejected(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen, patch('introduction.other_views.render') as render:
            cmd_lab3(request)

        popen.assert_not_called()
        render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Invalid domain'},
        )
