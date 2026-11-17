from unittest.mock import patch

from django.test import RequestFactory, TestCase
from types import SimpleNamespace

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def post_lookup(self, domain, os='win'):
        request = self.request_factory.post('/cmd_lab3/', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        response = other_views.cmd_lab3(self.post_lookup('example.com; whoami'))

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_is_passed_as_argument_without_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = other_views.cmd_lab3(self.post_lookup('https://www.example.com'))

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        process.communicate.assert_called_once_with()
        self.assertEqual(response.status_code, 200)
