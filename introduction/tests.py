from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess


class CommandInjectionLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab')

    def test_rejects_malicious_domain_before_subprocess(self):
        with patch('introduction.views.subprocess.run') as mock_run:
            response = self.client.post(self.url, {'domain': 'example.com; id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()

    def test_valid_domain_uses_argument_list_subprocess(self):
        with patch('introduction.views.subprocess.run') as mock_run:
            mock_run.return_value.stdout = 'example.com\n'
            mock_run.return_value.stderr = ''
            response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertContains(response, 'example.com')
