import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='cmduser', password='secure-pass-123')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_returns_lookup_output(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'example.com lookup ok\n', b'')
        mock_popen.return_value = process

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example.com lookup ok')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    @patch('introduction.other_views.subprocess.Popen')
    def test_shell_metacharacters_are_rejected_before_execution(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com;id', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Invalid domain', status_code=400)
        mock_popen.assert_not_called()
