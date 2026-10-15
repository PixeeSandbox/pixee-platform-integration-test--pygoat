from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com; id', 'os': 'linux'}
        )

        self.assertContains(response, 'Invalid domain. Please enter a valid hostname.')
        mock_popen.assert_not_called()
