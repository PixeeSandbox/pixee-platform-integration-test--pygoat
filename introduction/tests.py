import subprocess

from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        user = User.objects.create_user(username='tester', password='password123')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; whoami',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self):
        user = User.objects.create_user(username='tester2', password='password123')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_popen.return_value.communicate.return_value = (b'valid\n', b'')
            response = self.client.post('/cmd_lab3', {
                'domain': 'https://www.example.com',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'valid')
