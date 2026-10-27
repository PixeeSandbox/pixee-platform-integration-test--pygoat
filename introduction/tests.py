import subprocess

from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_without_shell(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'valid output', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertIn('valid output', response.content.decode())

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injected_domain(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
