import subprocess

from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            email='cmdlabuser@example.com',
            password='password123',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_for_windows_branch(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        self.client.force_login(self.user)
        domain = 'example.com;whoami'
        response = self.client.post('/cmd_lab', {'domain': domain, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', domain])
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], subprocess.PIPE)
        self.assertNotIn('shell', mock_popen.call_args.kwargs)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_for_non_windows_branch(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'dig output', b'')
        mock_popen.return_value = process

        self.client.force_login(self.user)
        domain = 'sub.example.com;whoami'
        response = self.client.post('/cmd_lab', {'domain': domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_args.args[0], ['dig', domain])
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], subprocess.PIPE)
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
