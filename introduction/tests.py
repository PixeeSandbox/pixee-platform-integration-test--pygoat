from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmdlab3user', password='password123')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; echo injected',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'injected')
