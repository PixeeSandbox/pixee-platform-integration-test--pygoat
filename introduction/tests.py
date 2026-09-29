from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import subprocess

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_rejects_unsafe_domain_without_calling_subprocess(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com; whoami', 'os': 'linux'}
        )
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_and_renders_output(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'valid output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'linux'}
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid output')
