import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, os='win'):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_hostname_with_shell_metacharacters(self, popen):
        response = self.post_cmd_lab('example.com; touch /tmp/injected')

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_uses_argument_list_without_a_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup result', b'')

        self.post_cmd_lab('example.com')

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
