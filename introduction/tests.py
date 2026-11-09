from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com; id', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
