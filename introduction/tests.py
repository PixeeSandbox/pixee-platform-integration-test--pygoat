from django.test import TestCase
from django.contrib.auth.models import User


class CmdLab3SecurityTests(TestCase):
    def test_rejects_malicious_domain_input(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
