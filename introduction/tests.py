import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_hostname_with_shell_metacharacters(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_resolves_valid_hostname_without_a_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'example.com', b'')

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.context['output'], 'example.com')
