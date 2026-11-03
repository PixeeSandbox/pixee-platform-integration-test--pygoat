from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_input(self):
        user = User.objects.create_user(username='secureuser', password='testpass123')
        self.client.force_login(user)

        malicious_domain = 'example.com; touch /tmp/pwned'
        response = self.client.post('/cmd_lab3', {'domain': malicious_domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        self.assertNotContains(response, malicious_domain)
