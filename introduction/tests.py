from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch
import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-test', password='password')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_injection_domain(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_passes_valid_domain_as_separate_arguments(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b' DNS output', b'')

        self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
