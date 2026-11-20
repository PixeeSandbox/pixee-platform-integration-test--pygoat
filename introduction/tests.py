import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_launching_process(self, popen):
        self.client.post('/cmd_lab', {'domain': 'example.com; touch /tmp/injected', 'os': 'win'})

        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_passed_as_separate_argument_without_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
