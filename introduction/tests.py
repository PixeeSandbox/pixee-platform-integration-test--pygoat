import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters_in_domain(self, mock_popen):
        self.client.post('/cmd_lab3', {'domain': 'example.com; touch /tmp/injected', 'os': 'linux'})

        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_non_shell_argument_list(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
