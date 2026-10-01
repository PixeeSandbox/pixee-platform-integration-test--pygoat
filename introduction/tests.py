import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='cmduser', password='Password123!')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_without_shell(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'example.com has address 93.184.216.34', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=__import__('subprocess').PIPE,
            stderr=__import__('subprocess').PIPE,
        )
        self.assertContains(response, 'example.com has address 93.184.216.34')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;rm -rf /', 'os': 'linux'})

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
