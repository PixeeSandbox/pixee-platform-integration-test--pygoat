import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd_test', password='test-password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_separate_command_arguments(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')

        self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_shell_metacharacters_are_rejected(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'linux'})

        mock_popen.assert_not_called()
        self.assertContains(response, 'Please enter a valid hostname.')
