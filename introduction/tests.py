from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
import subprocess
from unittest.mock import patch


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='command-test', password='password')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injection_shaped_domain(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com; whoami'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_passes_valid_domain_as_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
