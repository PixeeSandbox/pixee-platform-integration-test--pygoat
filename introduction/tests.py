import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com; whoami', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_safe_arguments_for_valid_hostname(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup ok', response.content)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
