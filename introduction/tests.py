import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_request(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        response = cmd_lab3(self.post_request('example.com; touch /tmp/injected'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_is_passed_as_separate_argument(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = cmd_lab3(self.post_request('example.com', os='win'))

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
