from types import SimpleNamespace
from unittest.mock import patch

import subprocess

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _request(self, domain, os_value='linux'):
        request = self.factory.post('/cmd_lab3', data={'domain': domain, 'os': os_value})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_popen(self, mock_popen):
        response = cmd_lab3(self._request('example.com;id'))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_invokes_popen_with_list_arguments_for_non_win(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'output', b'')

        response = cmd_lab3(self._request('example.com', 'linux'))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_invokes_nslookup_for_windows(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'output', b'')

        response = cmd_lab3(self._request('example.com', 'win'))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
