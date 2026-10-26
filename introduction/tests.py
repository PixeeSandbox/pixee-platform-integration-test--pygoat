from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_invoking_popen(self, mock_popen):
        response = self.client.post(
            '/cmd_lab',
            {
                'domain': 'https://www.example.com; whoami',
                'os': 'win',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok\n', b'')

        response = self.client.post(
            '/cmd_lab',
            {
                'domain': 'https://www.example.com',
                'os': 'win',
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertContains(response, 'lookup ok')
