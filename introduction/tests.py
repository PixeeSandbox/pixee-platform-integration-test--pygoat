import subprocess

from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters_and_uses_argv_list(self, mock_popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; echo hacked',
            'os': 'win',
        })
        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

        mock_popen.reset_mock()
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid output', b'')

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'win',
        })
        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
