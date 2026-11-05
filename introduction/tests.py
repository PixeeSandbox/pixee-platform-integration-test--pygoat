from unittest.mock import patch
import subprocess

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )

    def test_cmd_lab3_rejects_malicious_domain(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com', 'os': 'linux'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'example output', b'')

            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'example output')
