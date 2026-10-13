from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import subprocess

from django.test import RequestFactory, TestCase

import introduction.other_views as other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_and_no_shell_for_valid_domain(self, mock_popen, mock_render):
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process_mock
        mock_render.return_value = MagicMock()

        request = self.factory.post('/cmd_lab3', data={'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = MagicMock()

        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com; whoami', 'os': 'win'},
        )
        request.user = self.user

        other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
