import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test-user', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
