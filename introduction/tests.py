from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class CommandInjectionTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(user)

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com;id', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
