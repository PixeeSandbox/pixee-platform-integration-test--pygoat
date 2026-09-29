import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='testpass123',
        )
        self.client = Client()
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_safe_nslookup_invocation(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'nslookup ok\n', b'')

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'https://www.Example.com', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'nslookup ok')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com; cat /etc/passwd', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_safe_dig_invocation(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'dig ok\n', b'')

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'dig ok')
