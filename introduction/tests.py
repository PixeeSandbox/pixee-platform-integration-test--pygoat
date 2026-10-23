from unittest.mock import Mock, patch

import subprocess

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab3-user',
            password='password123',
        )

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, \
                patch('introduction.other_views.render', return_value=HttpResponse('ok')):
            process = Mock()
            process.communicate.return_value = (b'lookup ok', b'')
            mock_popen.return_value = process

            response = cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; whoami',
            'os': 'win',
        })
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, \
                patch('introduction.other_views.render', return_value=HttpResponse('bad')):
            response = cmd_lab3(request)

        self.assertEqual(response.content, b'bad')
        mock_popen.assert_not_called()
