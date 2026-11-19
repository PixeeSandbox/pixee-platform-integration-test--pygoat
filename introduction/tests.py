import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandLookupTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab')

    @patch('introduction.views.subprocess.Popen')
    def test_command_injection_domain_rejected(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Invalid domain', status_code=400)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_passed_as_arguments_and_result_rendered(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')

        response = self.client.post(self.url, {'domain': 'www.example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup result')
