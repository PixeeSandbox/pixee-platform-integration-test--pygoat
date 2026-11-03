import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            password='password123',
        )
        self.assertTrue(self.client.login(username='testuser', password='password123'))

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; rm -rf /',
                'os': 'linux',
            })

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argv_list_for_valid_hostname(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'valid output', b'')

            response = self.client.post('/cmd_lab', {
                'domain': 'example.com',
                'os': 'linux',
            })

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'valid output')
