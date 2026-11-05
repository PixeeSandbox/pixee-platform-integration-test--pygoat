import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.client.login(username='testuser', password='testpassword123')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_without_shell(self, mock_popen):
        malicious_domain = 'example.com; echo vulnerable'
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'nslookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': malicious_domain, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', malicious_domain])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertNotIn('shell', kwargs)
