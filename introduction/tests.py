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
    def test_cmd_lab3_valid_hostname_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok\n', b'')

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertContains(response, 'lookup ok')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_invalid_hostname_rejected_without_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; rm -rf /',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertContains(response, 'Invalid domain')
