import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmdtest', password='password')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_valid_hostname_runs_selected_executable(self, mock_run):
        mock_run.return_value.stdout = b'lookup output'
        mock_run.return_value.stderr = b'lookup warning'

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')
        self.assertContains(response, 'lookup warning')
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_hostname(self, mock_run):
        response = self.client.post(self.url, {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a valid domain')
        mock_run.assert_not_called()
