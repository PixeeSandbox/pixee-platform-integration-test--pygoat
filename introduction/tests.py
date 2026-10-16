from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

import subprocess

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    @patch('introduction.other_views.render', return_value=HttpResponse('rendered'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_injection_payload_before_subprocess(self, mock_popen, mock_render):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com; id', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_not_called()
        mock_render.assert_called_once()

    @patch('introduction.other_views.render', return_value=HttpResponse('rendered'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_argument_list_and_shell_false_for_valid_hostname(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once()
