from unittest.mock import patch
from types import SimpleNamespace

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from . import views


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def post_cmd_lab(self, domain, os_name='linux'):
        request = self.request_factory.post('/cmd_lab', {'domain': domain, 'os': os_name})
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.render', return_value=HttpResponse())
    @patch('introduction.views.subprocess.Popen')
    def test_domain_with_shell_syntax_is_rejected(self, popen, render):
        self.post_cmd_lab('example.com; touch /tmp/injected')

        popen.assert_not_called()
        self.assertEqual(render.call_args.args[2]['output'], 'Invalid domain')

    @patch('introduction.views.render', return_value=HttpResponse())
    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_without_shell(self, popen, render):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.post_cmd_lab('www.example.com', 'win')

        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
