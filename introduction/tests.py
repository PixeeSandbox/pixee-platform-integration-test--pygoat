import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, os='win'):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        self.post_cmd_lab('example.com; touch /tmp/injected')

        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_is_passed_as_separate_argument(self, popen):
        popen.return_value.communicate.return_value = (b'', b'')

        self.post_cmd_lab('https://www.example.com', os='win')

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
