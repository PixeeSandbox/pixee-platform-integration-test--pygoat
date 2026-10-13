import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_rejects_malicious_domain_without_invoking_subprocess(self):
        request = self.factory.post('/', {'domain': 'example.com;rm -rf /', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    def test_uses_argument_list_and_shell_false_for_benign_domain(self):
        request = self.factory.post('/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b'OK', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
