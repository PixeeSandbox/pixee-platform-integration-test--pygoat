from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from unittest.mock import ANY, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_benign_lookup_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'https://www.example.com', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=ANY,
            stderr=ANY,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_injection_payload_is_passed_as_single_argument(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'dig output', b'')

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'https://www.example.com; id', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com; id'],
            stdout=ANY,
            stderr=ANY,
        )
