from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_nslookup_list_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'ok', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {'os': 'win', 'domain': 'example.com'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_dig_list_for_non_win(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'ok', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {'os': 'linux', 'domain': 'example.org'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.org'])
        self.assertFalse(kwargs.get('shell', False))

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_strips_https_www_prefix_before_command_construction(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'ok', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {'os': 'win', 'domain': 'https://www.example.net'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.net'])
        self.assertFalse(kwargs.get('shell', False))
