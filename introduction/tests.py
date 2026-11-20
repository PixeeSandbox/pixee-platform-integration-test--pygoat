from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

import subprocess


class CommandInjectionTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd_test', password='test-password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_windows_submission_uses_argument_list(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_linux_submission_uses_argument_list(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'dig output', b'')

        self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_invalid_domain_is_rejected(self, mock_popen):
        response = self.client.post(
            '/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'}
        )

        self.assertEqual(response.context['output'], 'Invalid domain')
        mock_popen.assert_not_called()
