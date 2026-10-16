from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        User.objects.create_user(username='tester', password='pass12345')
        self.assertTrue(self.client.login(username='tester', password='pass12345'))

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com;id', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid input')
        self.assertNotContains(response, 'uid=')
