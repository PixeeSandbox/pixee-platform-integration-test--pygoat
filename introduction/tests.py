from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .views import is_valid_hostname


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain_input(self):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com;whoami', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')

    def test_hostname_validation_accepts_normal_hostname(self):
        self.assertTrue(is_valid_hostname('example.com'))
        self.assertTrue(is_valid_hostname('sub-domain.example.co.uk'))
        self.assertFalse(is_valid_hostname('example.com;whoami'))
