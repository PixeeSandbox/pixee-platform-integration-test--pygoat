import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='StrongPass123!'
        )
        self.assertTrue(
            self.client.login(username='cmdlab3user', password='StrongPass123!')
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain_before_command_execution(self, mock_run):
        response = self.client.post(
            '/cmd_lab3',
            {
                'domain': 'https://www.example.com;touch /tmp/pwned',
                'os': 'linux',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_allows_normal_hostname(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=['dig', 'example.com'],
            returncode=0,
            stdout=b'lookup ok',
            stderr=b''
        )

        response = self.client.post(
            '/cmd_lab3',
            {
                'domain': 'https://www.example.com',
                'os': 'linux',
            }
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'lookup ok')
