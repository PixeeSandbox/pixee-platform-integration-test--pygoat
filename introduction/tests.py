from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com; whoami', 'os': 'linux'}
        )
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)

    def test_cmd_lab3_uses_argument_list_without_shell_for_valid_domain(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'linux'}
        )
        request.user = SimpleNamespace(is_authenticated=True)

        process = SimpleNamespace(communicate=lambda: (b'lookup ok', b''))

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertIsInstance(args[0], list)
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertEqual(response.status_code, 200)
