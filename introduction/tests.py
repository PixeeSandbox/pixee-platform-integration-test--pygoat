from unittest.mock import ANY, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmdlab3user', password='testpass123')
        self.url = reverse('Command Injection Lab 3')

    def test_valid_hostname_uses_list_based_lookup(self):
        self.client.force_login(self.user)
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'lookup ok', b'')

            response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=ANY,
            stderr=ANY,
        )

    def test_malicious_domain_is_rejected_without_process_creation(self):
        self.client.force_login(self.user)
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post(self.url, {'domain': 'example.com; rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
