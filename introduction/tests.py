from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cmdlab3user', password='testpass123')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; whoami',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
