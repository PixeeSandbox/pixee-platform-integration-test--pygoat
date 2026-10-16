from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3RegressionTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='cmdlab3user',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_input(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com;id',
            'os': 'linux',
        })

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
