from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, os_choice='linux'):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os_choice})
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_invalid_domain_does_not_invoke_command_runner(self, popen):
        self.post_cmd_lab('example.com; touch /tmp/injected')

        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'answer', b'')

        self.post_cmd_lab('example.com', 'linux')

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
