from django.test import TestCase
from django.contrib.auth import get_user_model


class CmdLabSecurityTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain(self):
        user = get_user_model().objects.create_user(username='cmduser', password='password123')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab', {'domain': 'example.com; echo injected', 'os': 'linux'})

        self.assertContains(response, 'Invalid domain')
        self.assertNotContains(response, 'injected')
