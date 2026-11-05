import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_for_windows(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=['nslookup', 'example.com'],
            returncode=0,
            stdout='windows stdout',
            stderr='windows stderr',
        )
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'windows stdoutwindows stderr')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_for_linux(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=['dig', 'example.com'],
            returncode=0,
            stdout='linux stdout',
            stderr='linux stderr',
        )
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'linux stdoutlinux stderr')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_run):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
