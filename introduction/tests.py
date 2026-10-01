from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch

import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='secure-password-123'
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_dig_without_shell(self, mock_popen):
        self.client.force_login(self.user)
        mock_popen.return_value.communicate.return_value = (b'dig output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_nslookup_without_shell(self, mock_popen):
        self.client.force_login(self.user)
        mock_popen.return_value.communicate.return_value = (b'nslookup output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_invalid_domain_without_popen(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
