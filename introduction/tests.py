import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_invalid_hostname_shell_syntax_is_rejected_without_process(self, popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_uses_fixed_executable_and_argument(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
