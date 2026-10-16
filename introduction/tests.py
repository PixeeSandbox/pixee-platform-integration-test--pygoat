import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_and_uses_safe_subprocess_args(self, mock_popen):
        invalid_request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        invalid_request.user = self.user

        invalid_response = views.cmd_lab(invalid_request)

        self.assertEqual(invalid_response.status_code, 200)
        self.assertIn('Something went wrong', invalid_response.content.decode())
        mock_popen.assert_not_called()

        process = MagicMock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        valid_request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com', 'os': 'linux'},
        )
        valid_request.user = self.user

        valid_response = views.cmd_lab(valid_request)

        self.assertEqual(valid_response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIn('lookup ok', valid_response.content.decode())
