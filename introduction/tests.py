from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='cmdtester', password='password123')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain(self):
        with patch('introduction.other_views.subprocess.Popen') as popen_mock:
            response = self.client.post(
                '/cmd_lab3',
                {'domain': 'https://www.example.com;whoami', 'os': 'win'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        popen_mock.assert_not_called()
