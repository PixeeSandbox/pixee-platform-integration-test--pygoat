import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def post_cmd_lab(self, domain, os_selector='linux'):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os_selector})
        request.user = self.user
        return cmd_lab(request)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_starting_process(self, popen, render):
        response = self.post_cmd_lab('example.com; touch /tmp/pwned')

        popen.assert_not_called()
        render.assert_called_once()
        self.assertIs(response, render.return_value)
        self.assertEqual(render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(render.call_args.args[2], {"output": "Something went wrong"})

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_invokes_fixed_executable_with_domain_argument_without_shell(self, popen, render):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        render.return_value = object()

        response = self.post_cmd_lab('example.com', 'linux')

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.communicate.assert_called_once_with()
        render.assert_called_once()
        self.assertIs(response, render.return_value)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_rejects_unsupported_os_selector(self, popen, render):
        self.post_cmd_lab('example.com', 'other')

        popen.assert_not_called()
        render.assert_called_once()
