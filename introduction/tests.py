from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain_input(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.run') as mock_run:
            response = self.client.post(
                reverse('Command Injection Lab'),
                {'domain': 'example.com; whoami', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()
