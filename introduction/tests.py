import subprocess

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_windows_nslookup(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'nslookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_passes_malicious_domain_as_single_argument(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'dig output', b'')
        malicious_domain = 'https://www.example.com; touch /tmp/pwned && whoami'

        response = self.client.post('/cmd_lab', {'domain': malicious_domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com; touch /tmp/pwned && whoami'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
