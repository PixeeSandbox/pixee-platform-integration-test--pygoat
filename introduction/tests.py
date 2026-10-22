import subprocess
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'https://www.example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_safe_argument_list(self):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'https://www.example.com', 'os': 'linux'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'example output', b'')

            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
