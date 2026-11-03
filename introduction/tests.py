from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock
import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )
        self.url = '/cmd_lab3'

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_list_invocation_for_benign_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        self.client.force_login(self.user)
        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'domain': 'example.com; rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
