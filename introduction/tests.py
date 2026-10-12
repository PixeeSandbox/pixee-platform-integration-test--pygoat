import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, mock_popen):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com; whoami', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_dig_with_argument_list_for_linux(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'linux output', b'')

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_nslookup_with_argument_list_for_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'windows output', b'')

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
