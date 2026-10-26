from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3
import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_popen(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com;id', 'os': 'win'}
        )
        request.user = SimpleNamespace(is_authenticated=True)
        request.session = {}

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_and_shell_false_for_valid_domain(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com', 'os': 'win'}
        )
        request.user = SimpleNamespace(is_authenticated=True)
        request.session = {}

        process = MagicMock()
        process.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIn(b'lookup ok', response.content)
