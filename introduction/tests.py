import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_domain(self, domain, os='linux'):
        request = self.factory.post('/cmd/', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab3(request)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_passed_as_argument_without_shell(self, popen, render):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        self.post_domain('example.com')

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_shell_metacharacters_are_rejected(self, popen, render):
        self.post_domain('example.com; touch /tmp/injected')

        popen.assert_not_called()
        render.assert_called_once()
        self.assertEqual(render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(render.call_args.args[2], {'output': 'Something went wrong'})
