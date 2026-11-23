from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_runs_valid_domain_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'example.com', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
