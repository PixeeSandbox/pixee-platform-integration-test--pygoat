from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_input(self):
        user = User.objects.create_user(username='cmdlab3user', password='pass12345')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'uid=')
