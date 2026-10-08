from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='StrongPassword123!'
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_injection_payload(self):
        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com;id', 'os': 'win'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid domain')
        self.assertContains(response, 'Invalid domain')
