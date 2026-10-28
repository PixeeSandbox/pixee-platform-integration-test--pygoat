import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password')

    def test_cmd_lab3_rejects_malicious_domain_without_running_command(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com; id', 'os': 'linux'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)

    def test_cmd_lab3_uses_argument_list_without_shell_for_valid_domain(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'linux'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as popen:
            popen.return_value.communicate.return_value = (b'answer', b'')
            response = cmd_lab3(request)

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'answer', response.content)
