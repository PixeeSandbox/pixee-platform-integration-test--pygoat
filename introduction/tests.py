import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='password123'
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_shell_false(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'lookup output', b'')

        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIn(b'lookup output', response.content)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertIn(b'Invalid domain', response.content)
