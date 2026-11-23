import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client = Client()
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_is_passed_as_a_separate_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_shell_metacharacters_in_domain_are_rejected(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com;whoami', 'os': 'linux'})

        mock_popen.assert_not_called()
        self.assertEqual(response.context['output'], 'Invalid domain')
