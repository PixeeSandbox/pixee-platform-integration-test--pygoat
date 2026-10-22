from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
import subprocess
from unittest.mock import patch

from introduction.other_views import cmd_lab3
from introduction.views import cmd_lab


class CommandInjectionRemediationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )

    def _authenticated_post(self, path, data):
        request = self.factory.post(path, data=data)
        request.user = self.user
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_post_uses_argv_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'nslookup output', b'')
        request = self._authenticated_post(
            '/cmd_lab3/',
            {'domain': 'example.com', 'os': 'win'},
        )

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_popen.call_args[0][0], ['nslookup', 'example.com'])
        self.assertFalse('shell' in mock_popen.call_args[1])
        self.assertEqual(mock_popen.call_args[1]['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args[1]['stderr'], subprocess.PIPE)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_valid_post_uses_argv_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'dig output', b'')
        request = self._authenticated_post(
            '/cmd_lab/',
            {'domain': 'example.com', 'os': 'linux'},
        )

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertFalse('shell' in mock_popen.call_args[1])
        self.assertEqual(mock_popen.call_args[1]['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args[1]['stderr'], subprocess.PIPE)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen):
        request = self._authenticated_post(
            '/cmd_lab3/',
            {'domain': 'example.com; rm -rf /', 'os': 'win'},
        )

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_count, 0)
        self.assertIn(b'Something went wrong', response.content)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, mock_popen):
        request = self._authenticated_post(
            '/cmd_lab/',
            {'domain': 'example.com && whoami', 'os': 'linux'},
        )

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_count, 0)
        self.assertIn(b'Something went wrong', response.content)
