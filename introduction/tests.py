import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-lab-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_syntax_without_process(self, popen):
        self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})

        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_uses_fixed_lookup_arguments_for_valid_domain(self, popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        popen.return_value = process

        self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
