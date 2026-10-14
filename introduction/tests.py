import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_for_linux_domain(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'linux output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'linux output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_for_windows_domain(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'windows output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.org', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.org'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'windows output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
