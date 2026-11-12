from types import SimpleNamespace
from unittest.mock import patch

import subprocess
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_domain(self, domain, os='win'):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_passed_as_separate_argument(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup result', b'')

        self.post_domain('example.com', 'win')

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_invalid_domains_are_rejected_without_process(self, popen):
        for domain in ('example.com;id', '-example.com'):
            with self.subTest(domain=domain):
                self.post_domain(domain)

        popen.assert_not_called()
