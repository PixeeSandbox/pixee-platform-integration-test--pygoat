import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_for_dig(self, mock_popen):
        process = SimpleNamespace(communicate=lambda: (b'dig output', b''))
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; whoami', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com; whoami'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_nslookup_on_windows(self, mock_popen):
        process = SimpleNamespace(communicate=lambda: (b'nslookup output', b''))
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com&&id', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com&&id'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
