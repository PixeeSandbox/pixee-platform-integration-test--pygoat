from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(self.user)
        self.url = '/cmd_lab'

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_for_windows_branch(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'windows-ok', b'')
        mock_popen.return_value = process

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_for_non_windows_branch(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'linux-ok', b'')
        mock_popen.return_value = process

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_invalid_domain_before_process_execution(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
