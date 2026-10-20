import subprocess

from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_shell_false_for_safe_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'stdout', b'stderr')

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertEqual(kwargs['shell'], False)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertContains(response, 'stdout')
        self.assertContains(response, 'stderr')
