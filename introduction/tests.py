from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

import subprocess

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, popen_mock, render_mock):
        render_mock.return_value = HttpResponse('blocked')
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
        self.assertEqual(response.content, b'blocked')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_executes_argument_list_without_shell(self, popen_mock, render_mock):
        process = MagicMock()
        process.communicate.return_value = (b'dns output', b'')
        popen_mock.return_value = process
        render_mock.return_value = HttpResponse('ok')
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'dns output'},
        )
        self.assertEqual(response.content, b'ok')
