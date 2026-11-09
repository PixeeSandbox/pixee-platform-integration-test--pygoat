from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com;whoami', 'os': 'win'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain name')
        mock_run.assert_not_called()
