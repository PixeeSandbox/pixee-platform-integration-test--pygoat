import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='pass12345')

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain_without_subprocess(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_argument_list_and_no_shell_for_valid_domain(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'output', b'')

        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
