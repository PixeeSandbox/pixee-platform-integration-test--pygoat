import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_invalid_domain_without_running_process(self, mock_popen):
        for domain in ('example.com; touch /tmp/pwned', '-example.com'):
            with self.subTest(domain=domain):
                response = self.client.post(self.url, {'domain': domain, 'os': 'win'})
                self.assertEqual(response.status_code, 400)

        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_fixed_command_and_renders_output(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'Name: example.com', b'')

        response = self.client.post(self.url, {'domain': 'https://www.example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Name: example.com')
