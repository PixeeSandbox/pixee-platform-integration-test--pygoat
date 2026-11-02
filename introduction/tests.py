import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab-user',
            password='test-password'
        )

    def _build_request(self, domain, os_value='linux'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = cmd_lab3(self._build_request('example.com', 'linux'))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertEqual(kwargs, {'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE})
        self.assertNotIn(b'Invalid input', response.content)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = cmd_lab3(self._build_request('example.com; rm -rf /', 'linux'))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn(b'Invalid input', response.content)
