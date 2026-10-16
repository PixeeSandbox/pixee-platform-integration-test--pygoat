import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_safe_argv_for_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'nslookup output', b'')
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'nslookup output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_safe_argv_for_non_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'dig output', b'')
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'dig output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com;rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
