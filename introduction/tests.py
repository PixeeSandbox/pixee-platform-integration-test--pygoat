from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class CommandInjectionTests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_input(self):
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(user)

        response = self.client.post(reverse('Command Injection Lab 3'), {
            'domain': 'example.com;id',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
