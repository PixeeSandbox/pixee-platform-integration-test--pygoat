import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-test', password='password')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_invalid_domain(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
