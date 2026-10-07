import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')

    def _build_request(self, domain, os_choice):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os_choice})
        request.user = self.user
        return request

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value.stdout = b'example output\n'
        mock_run.return_value.stderr = b''
        request = self._build_request('https://www.example.com', 'linux')

        response = cmd_lab(request)

        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'example output', response.content)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_blocks_malicious_domain(self, mock_run):
        request = self._build_request('https://www.example.com; id', 'linux')

        response = cmd_lab(request)

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
