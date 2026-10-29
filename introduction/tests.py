import subprocess
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_without_shell(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'normal output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
