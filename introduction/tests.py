from django.test import TestCase
from django.contrib.auth.models import User


class CommandInjectionTests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(user)
        response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'win'})
        self.assertContains(response, 'Something went wrong')
