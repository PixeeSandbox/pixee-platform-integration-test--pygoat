from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain(self):
        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com; rm -rf /', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
