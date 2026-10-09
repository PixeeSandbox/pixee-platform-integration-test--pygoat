import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )

    def _build_request(self, domain, os_value='win'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain_before_subprocess_is_called(self, mock_popen):
        request = self._build_request('example.com; rm -rf /', 'win')

        response = cmd_lab3(request)

        self.assertFalse(mock_popen.called)
        self.assertEqual(response.status_code, 200)

    @patch('introduction.other_views.subprocess.Popen')
    def test_invokes_subprocess_with_safe_argument_list(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process
        request = self._build_request('example.com', 'win')

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
