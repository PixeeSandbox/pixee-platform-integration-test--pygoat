import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CommandInjectionRegressionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd(self, domain, os_value='linux'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os_value})
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab3(request)

    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_domain_is_rejected_without_launching_process(self, popen):
        response = self.post_cmd('example.com; touch /tmp/injected')

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_and_separate_argument(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.post_cmd('https://www.example.com', 'win')

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.communicate.assert_called_once_with()
