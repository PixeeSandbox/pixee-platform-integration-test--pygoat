import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmdlab3', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_list_arguments(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'mock output', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'mock output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_popen(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid domain provided', status_code=400)
