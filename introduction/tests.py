from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch
from subprocess import CompletedProcess

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess_call(self, mock_run):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_run.called)
        self.assertContains(response, 'Something went wrong')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = CompletedProcess(
            args=['dig', 'example.com'],
            returncode=0,
            stdout='lookup output',
            stderr=''
        )
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            capture_output=True,
            text=True,
        )
        self.assertContains(response, 'lookup output')
