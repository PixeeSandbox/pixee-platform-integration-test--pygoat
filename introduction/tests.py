import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3ViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='secure-password-123',
        )
        logged_in = self.client.login(username='cmdlab3user', password='secure-password-123')
        self.assertTrue(logged_in)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'safe-output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
