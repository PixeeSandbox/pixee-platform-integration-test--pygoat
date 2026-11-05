from django.test import TestCase, RequestFactory
from unittest.mock import patch
import subprocess

from django.contrib.auth import get_user_model

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'https://www.example.com;id', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'valid output', b'')

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'https://www.example.com', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'valid output', response.content)
