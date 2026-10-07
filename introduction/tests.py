from unittest.mock import patch
import subprocess

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='strong-password-123',
        )
        self.client.force_login(self.user)

    def test_cmd_lab_uses_argument_list_without_shell(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'good', b'')

            response = self.client.post('/cmd_lab', {
                'domain': 'https://www.example.com',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertIn(b'good', response.content)

    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'https://www.example.com;rm -rf /',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn(b'Something went wrong', response.content)
