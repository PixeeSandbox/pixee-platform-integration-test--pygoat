import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmd_lab3_user', password='test-password'
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_hostname_with_shell_metacharacters(self, popen):
        response = self.client.post(
            '/cmd_lab3', {'domain': 'example.com;whoami', 'os': 'win'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_runs_valid_hostname_without_a_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup result', b'')

        response = self.client.post(
            '/cmd_lab3', {'domain': 'www.example.com', 'os': 'win'}
        )

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.context['output'], 'lookup result')
