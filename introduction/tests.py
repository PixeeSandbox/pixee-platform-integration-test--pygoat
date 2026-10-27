import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123'
        )

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'https://www.example.com; rm -rf /', 'os': 'win'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(mock_popen.called)

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'https://www.example.com', 'os': 'win'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'example output', b'')

            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
