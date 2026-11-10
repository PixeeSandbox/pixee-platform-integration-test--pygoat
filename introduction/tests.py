from unittest.mock import patch

import subprocess
from django.test import RequestFactory, TestCase
from types import SimpleNamespace

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_lookup(self, domain, operating_system='linux'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': operating_system})
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab3(request)

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_is_passed_as_argument_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.post_lookup('example.com')

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_windows_lookup_uses_fixed_executable(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.post_lookup('example.com', 'win')

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_malformed_domain_is_rejected_without_subprocess(self, mock_popen):
        response = self.post_lookup('example.com;whoami')

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_missing_domain_is_rejected_without_subprocess(self, mock_popen):
        response = self.post_lookup(None)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
