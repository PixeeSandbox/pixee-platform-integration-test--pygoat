import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_without_executing_command(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com;whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'output', b'')
            response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
