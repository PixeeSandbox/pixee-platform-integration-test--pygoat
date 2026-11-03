from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_windows_uses_argument_list_and_shell_false(self, mock_popen):
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b'windows output', b'')
        domain = 'example.com; whoami && cat /etc/passwd'
        response = self.client.post('/cmd_lab3', {'domain': domain, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', domain])
        self.assertFalse(kwargs['shell'])

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_unix_uses_argument_list_and_shell_false(self, mock_popen):
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b'unix output', b'')
        domain = 'example.org; uname -a'
        response = self.client.post('/cmd_lab3', {'domain': domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', domain])
        self.assertFalse(kwargs['shell'])
