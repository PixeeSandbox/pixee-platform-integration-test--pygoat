import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3CommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_request(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os})
        request.user = Mock(is_authenticated=True)
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_injection_without_launching_subprocess(self, popen, render):
        cmd_lab3(self.post_request('example.com; whoami'))

        popen.assert_not_called()
        render.assert_called_once()
        self.assertEqual(render.call_args.args[2], {'output': 'Invalid domain'})

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, popen, render):
        process = Mock()
        process.communicate.return_value = (b'lookup result', b'')
        popen.return_value = process

        cmd_lab3(self.post_request('example.com'))

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.communicate.assert_called_once_with()
        self.assertEqual(render.call_args.args[2], {'output': 'lookup result'})
