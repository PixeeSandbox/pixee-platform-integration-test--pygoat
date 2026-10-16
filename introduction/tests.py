from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain_input(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(user)

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com;id', 'os': 'win'}
        )

        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.status_code, 400)
