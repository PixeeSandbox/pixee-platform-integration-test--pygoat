from django.test import TestCase
from django.contrib.auth import get_user_model
import subprocess
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='testuser', password='password123')
        self.assertTrue(self.client.login(username='testuser', password='password123'))

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com && whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
