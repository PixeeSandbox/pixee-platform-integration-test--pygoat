import subprocess

from django.test import TestCase, RequestFactory
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _authenticated_post(self, data):
        request = self.factory.post('/cmd_lab3/', data=data)
        request.user = type('User', (), {'is_authenticated': True})()
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        request = self._authenticated_post({'domain': 'example.com;rm -rf /', 'os': 'win'})

        cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Invalid domain')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_non_shell_argument_list_for_valid_domain(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        request = self._authenticated_post({'domain': 'example.com', 'os': 'win'})

        cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'lookup output')
