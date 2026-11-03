from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.run') as mock_run:
            response = self.client.post(
                reverse('Command Injection Lab 3'),
                {'domain': 'example.com; cat /etc/passwd', 'os': 'win'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()
