import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_syntax_before_running_command(self, mock_popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {
            'domain': 'sub.example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'sub.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
