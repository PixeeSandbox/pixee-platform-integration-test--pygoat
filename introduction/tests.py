from subprocess import PIPE
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_runs_fixed_executable_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=PIPE,
            stderr=PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')

    @patch('introduction.views.subprocess.Popen')
    def test_domain_with_shell_metacharacters_is_rejected(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'linux'})

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
