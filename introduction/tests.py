from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch
import subprocess

from introduction.views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self):
        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'}
        )
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_and_shell_false_for_valid_domain(self):
        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com', 'os': 'linux'}
        )
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_popen.return_value.communicate.return_value = (b'output', b'')

            response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
