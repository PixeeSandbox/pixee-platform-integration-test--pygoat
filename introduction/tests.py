import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmdtest', password='test-password')
        self.client.force_login(user)
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters_in_hostname(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid hostname')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_passes_valid_hostname_as_literal_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
