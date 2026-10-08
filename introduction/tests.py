from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        url = reverse('Command Injection Lab 3')
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                url,
                {'domain': 'example.com; whoami', 'os': 'win'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
