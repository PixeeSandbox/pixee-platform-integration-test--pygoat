import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='password123')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_safe_argument_list(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'example.com has address 93.184.216.34\n', b'')
        mock_popen.return_value = process

        self.client.force_login(self.user)
        response = self.client.post('/cmd_lab', {'domain': 'https://www.Example.com.', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        self.client.force_login(self.user)
        response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
