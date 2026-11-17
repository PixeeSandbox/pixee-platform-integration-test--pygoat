from unittest.mock import patch
import subprocess

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_running_command(self, popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; touch /tmp/pwned',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_runs_valid_hostname_without_a_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'lookup result')
