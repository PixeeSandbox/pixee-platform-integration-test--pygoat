from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch
import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_looks_up_valid_hostname_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'example.com', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example.com')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
