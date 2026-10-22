from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import Mock, patch
import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'windows-output', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertContains(response, 'windows-output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_default_branch(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'linux-output', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertContains(response, 'linux-output')
