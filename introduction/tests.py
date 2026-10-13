import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell_for_valid_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertNotIn('shell', kwargs)
        self.assertContains(response, 'lookup output')
