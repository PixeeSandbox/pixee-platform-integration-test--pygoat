import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123'
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_windows_branch_uses_argument_list(self, mock_popen, mock_render):
        malicious_domain = 'example.com; whoami && echo injected'
        request = self.factory.post('/cmd_lab3', data={'domain': malicious_domain, 'os': 'win'})
        request.user = self.user

        process = Mock()
        process.communicate.return_value = ('windows output', 'windows error')
        mock_popen.return_value = process
        mock_render.return_value = Mock()

        cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', malicious_domain],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_non_windows_branch_uses_argument_list(self, mock_popen, mock_render):
        malicious_domain = 'example.org; whoami && echo injected'
        request = self.factory.post('/cmd_lab3', data={'domain': malicious_domain, 'os': 'linux'})
        request.user = self.user

        process = Mock()
        process.communicate.return_value = ('linux output', 'linux error')
        mock_popen.return_value = process
        mock_render.return_value = Mock()

        cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['dig', malicious_domain],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
