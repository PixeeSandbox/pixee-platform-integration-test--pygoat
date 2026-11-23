import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-test-user', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_is_passed_as_separate_arguments(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'answer', b'')

        self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_hostile_domain_is_rejected_before_execution(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})

        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid hostname')

    @patch('introduction.views.subprocess.Popen')
    def test_option_like_hostname_is_rejected_before_execution(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': '--help', 'os': 'linux'})

        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid hostname')
