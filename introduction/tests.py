import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_linux_uses_argument_list(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'linux output', b'')

        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'linux output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_windows_uses_nslookup_argument_list(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'windows output', b'')

        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'windows output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
