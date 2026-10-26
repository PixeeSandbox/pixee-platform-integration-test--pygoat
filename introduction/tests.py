from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch
import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='testuser', password='StrongPass123!')
        self.assertTrue(self.client.login(username='testuser', password='StrongPass123!'))

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'OK', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertEqual(kwargs.get('stdout'), subprocess.PIPE)
        self.assertEqual(kwargs.get('stderr'), subprocess.PIPE)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
