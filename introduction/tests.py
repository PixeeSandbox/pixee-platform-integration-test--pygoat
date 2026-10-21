from django.test import TestCase, RequestFactory
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com; rm -rf /', 'os': 'win'}
        )
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid input', response.content.decode('utf-8'))
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_and_renders_output_for_valid_hostname(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'win'}
        )
        request.user = SimpleNamespace(is_authenticated=True)

        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'command output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=mock_process) as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        call_args, call_kwargs = mock_popen.call_args
        self.assertIsInstance(call_args[0], list)
        self.assertEqual(call_args[0], ['nslookup', 'example.com'])
        self.assertFalse(call_kwargs.get('shell', False))
        self.assertIn('command output', response.content.decode('utf-8'))
