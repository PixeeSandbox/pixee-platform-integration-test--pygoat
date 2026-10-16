from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(reverse('Command Injection Lab 3'), {
            'domain': 'example.com;id',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_allows_valid_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example.com lookup output', b'')

        response = self.client.post(reverse('Command Injection Lab 3'), {
            'domain': 'https://www.example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertContains(response, 'example.com lookup output')
