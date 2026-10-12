import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_non_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab/',
            data={'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com; rm -rf /'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab/',
            data={'domain': 'example.com && whoami', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com && whoami'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
