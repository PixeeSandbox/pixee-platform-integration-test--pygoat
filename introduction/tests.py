from unittest.mock import ANY, Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_shell_execution(self, mock_popen):
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {
                'domain': 'example.com; touch /tmp/pwned',
                'os': 'win',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_style_subprocess_invocation(self, mock_popen):
        self.client.login(username='testuser', password='testpass123')
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {
                'domain': 'https://www.example.com',
                'os': 'win',
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertContains(response, 'lookup output')
