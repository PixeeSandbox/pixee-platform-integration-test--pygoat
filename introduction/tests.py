from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_cmd_lab3_rejects_malicious_domain(self):
        self.assertTrue(self.client.login(username='tester', password='password123'))
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'linux'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')

    def test_cmd_lab3_accepts_hostname_like_domain(self):
        self.assertTrue(self.client.login(username='tester', password='password123'))
        response = self.client.post('/cmd_lab3', {'domain': 'localhost', 'os': 'linux'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Invalid domain')
