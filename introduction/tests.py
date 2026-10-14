import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='secret123')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_argument_list_and_shell_false(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        self.client.force_login(self.user)
        response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', True))
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertContains(response, 'lookup output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        self.client.force_login(self.user)
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
