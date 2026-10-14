import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_nslookup_without_shell_for_windows_branch(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'windows-output', b'')

        malicious_domain = 'example.com; whoami'
        response = self.client.post('/cmd_lab3', {
            'domain': malicious_domain,
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', malicious_domain])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertNotIn('shell', kwargs)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_dig_without_shell_for_non_windows_branch(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'linux-output', b'')

        domain = 'https://www.example.org'
        response = self.client.post('/cmd_lab3', {
            'domain': domain,
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.org'])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertNotIn('shell', kwargs)
