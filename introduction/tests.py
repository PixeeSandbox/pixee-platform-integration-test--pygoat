from django.test import TestCase, RequestFactory
from types import SimpleNamespace
from unittest.mock import patch
import subprocess

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        mock_render.return_value = SimpleNamespace()

        cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Invalid domain')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = SimpleNamespace(communicate=lambda: (b'lookup output', b''))
        mock_popen.return_value = process
        mock_render.return_value = SimpleNamespace()
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'lookup output')
