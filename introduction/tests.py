import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123'
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_without_shell_for_valid_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')

        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
