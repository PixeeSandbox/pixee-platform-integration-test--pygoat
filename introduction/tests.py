import subprocess

from django.test import TestCase, RequestFactory
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build_request(self, domain, os_value):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os_value})
        request.user = type('User', (), {'is_authenticated': True})()
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_structured_subprocess_arguments(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid output', b'')
        mock_render.return_value = 'rendered-response'

        request = self._build_request('example.com', 'win')
        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'valid output'}
        )
        self.assertEqual(response, 'rendered-response')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = 'rendered-error-response'

        request = self._build_request('example.com;id', 'linux')
        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'}
        )
        self.assertEqual(response, 'rendered-error-response')
