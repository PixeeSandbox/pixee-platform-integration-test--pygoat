from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

import introduction.other_views

import subprocess
import yaml


class CmdLab3ViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _request(self, domain, os_value='win'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os_value})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain_without_popen(self, mock_popen, mock_render):
        mock_render.return_value = object()

        request = self._request('https://www.example.com;id', 'win')
        response = introduction.other_views.cmd_lab3(request)

        self.assertIs(response, mock_render.return_value)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Invalid domain'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_argv_list_without_shell_for_valid_domain(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'line1', b'')
        mock_render.return_value = object()

        request = self._request('https://www.example.com', 'win')
        response = introduction.other_views.cmd_lab3(request)

        self.assertIs(response, mock_render.return_value)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_once()


if __name__ == '__main__':
    stream = open('/home/fox/test.yaml', 'r')
    data = yaml.load(stream)
    print(data + "\n")
