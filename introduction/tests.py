from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import subprocess

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def _build_request(self, domain, os_value):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': domain, 'os': os_value},
        )
        request.user = self.user
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_domain_blocks_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = MagicMock()
        request = self._build_request('example.com;rm -rf /', 'win')

        response = cmd_lab3(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_not_called()
        mock_render.assert_called_once()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list(self, mock_popen, mock_render):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = mock_process
        mock_render.return_value = MagicMock()
        request = self._build_request('example.com', 'win')

        response = cmd_lab3(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
