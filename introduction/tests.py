import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandLab3Tests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_invokes_fixed_executable_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.client.post(reverse('Command Injection Lab 3'), {
            'domain': 'example.com',
            'os': 'win',
        })

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_malformed_hostname_does_not_launch_subprocess(self, mock_popen):
        response = self.client.post(reverse('Command Injection Lab 3'), {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        })

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
