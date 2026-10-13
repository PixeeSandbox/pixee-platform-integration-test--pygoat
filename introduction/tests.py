from types import SimpleNamespace
from unittest.mock import Mock, patch

import subprocess

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build_request(self, domain, os_value='win'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os_value})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        request = self._build_request('https://www.example.com', 'win')
        response = cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once()

    @patch('introduction.other_views.render', return_value=HttpResponse('bad'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_popen, mock_render):
        request = self._build_request('https://www.example.com; rm -rf /', 'win')
        response = cmd_lab3(request)

        self.assertEqual(response.content, b'bad')
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Something went wrong')
