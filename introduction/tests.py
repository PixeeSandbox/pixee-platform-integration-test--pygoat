from unittest.mock import patch
import subprocess

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_is_passed_as_separate_argument(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_shell_metacharacters_are_rejected(self, popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context['output'], 'Invalid domain name')
        popen.assert_not_called()
