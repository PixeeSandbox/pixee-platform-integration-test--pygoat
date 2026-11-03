import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_windows_branch(self, mock_popen):
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = ('windows lookup output', '')

        domain = 'example.com; rm -rf /'
        response = self.client.post('/cmd_lab3', {'domain': domain, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_non_windows_branch(self, mock_popen):
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = ('non windows lookup output', '')

        domain = 'example.org && whoami'
        response = self.client.post('/cmd_lab3', {'domain': domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )
