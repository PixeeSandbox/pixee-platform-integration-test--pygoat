import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab 3")

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'answer', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_shell_syntax_in_domain_is_rejected(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
