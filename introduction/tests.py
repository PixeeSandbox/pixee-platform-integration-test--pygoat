import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_normalizes_domain_and_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'ok', b'')

        response = self.client.post(
            '/cmd_lab',
            {'domain': 'https://www.Example.COM', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_invalid_domain_before_execution(self, mock_popen):
        response = self.client.post(
            '/cmd_lab',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
