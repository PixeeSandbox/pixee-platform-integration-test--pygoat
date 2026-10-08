from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com;whoami', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_allows_normal_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = ('lookup ok', '')

        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=-1,
            stderr=-1,
            text=True,
        )
