import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd_lab_user', password='test-password')
        self.client.force_login(self.user)

    def test_valid_hostname_uses_fixed_executable_and_argument_list(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_popen.return_value.communicate.return_value = (b'output', b'')

            self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_shell_metacharacters_are_rejected(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'win'})

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
