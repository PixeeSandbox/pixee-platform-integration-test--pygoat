import subprocess
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_lookup(self, domain, os='win'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.other_views.render')
    def test_rejects_shell_metacharacters_without_starting_process(self, mock_render, mock_popen):
        request = self.post_lookup('example.com; whoami')

        cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Something went wrong')

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.other_views.render')
    def test_valid_hostname_is_passed_as_argument_without_shell(self, mock_render, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        request = self.post_lookup('www.example.com')

        cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
