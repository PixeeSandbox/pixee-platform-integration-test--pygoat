import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)
        self.url = '/cmd_lab3'

    @patch('introduction.other_views.subprocess.Popen')
    def test_invalid_domain_rejected_without_popen(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain supplied')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_safe_domain_uses_argument_list_and_shell_false(self, mock_popen):
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b'lookup output', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'lookup output')
