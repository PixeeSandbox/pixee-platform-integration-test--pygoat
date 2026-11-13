from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')

    def test_valid_hostname_uses_argument_list_without_shell(self):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as popen:
            popen.return_value.communicate.return_value = (b'lookup output', b'')
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_shell_syntax_domain_is_rejected_before_execution(self):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com;whoami',
            'os': 'linux',
        })
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
