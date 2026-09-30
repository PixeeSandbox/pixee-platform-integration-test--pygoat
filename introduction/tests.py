import subprocess
from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                '/cmd_lab3',
                {'domain': 'example.com;whoami', 'os': 'linux'},
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain provided')
        self.assertFalse(mock_popen.called)

    def test_cmd_lab3_accepts_valid_hostname(self):
        process = MagicMock()
        process.communicate.return_value = (b'valid output', b'')
        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post(
                '/cmd_lab3',
                {'domain': 'example.com', 'os': 'linux'},
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid output')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
