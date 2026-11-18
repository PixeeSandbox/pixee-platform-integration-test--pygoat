from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User(username='testuser')

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_and_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')
        request = self.factory.post('/cmd/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_non_windows_uses_dig(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')
        request = self.factory.post('/cmd/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_injection_shaped_domain_is_rejected(self, mock_popen):
        request = self.factory.post('/cmd/', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
