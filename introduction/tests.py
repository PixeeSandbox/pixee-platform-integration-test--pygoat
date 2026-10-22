import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_cmd_lab_safe_domain_uses_argument_list_without_shell(self):
        self.client.force_login(self.user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'lookup ok', b'')

            response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'lin'})

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'lookup ok')

    def test_cmd_lab_rejects_shell_metacharacters(self):
        self.client.force_login(self.user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'lin'})

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Something went wrong')
