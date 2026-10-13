import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.assertTrue(self.client.login(username='cmduser', password='password123'))

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_without_shell_for_benign_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab', {'domain': 'https://www.Example.com.', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'example output', response.content)
        mock_popen.assert_called_once_with(['dig', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_and_skips_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; cat /etc/passwd', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mock_popen.assert_not_called()
