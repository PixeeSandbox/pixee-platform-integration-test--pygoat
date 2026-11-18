from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(user)

        response = self.client.post(reverse('Command Injection Lab 3'), {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
