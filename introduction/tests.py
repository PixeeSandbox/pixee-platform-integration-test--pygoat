from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='securitytester', password='StrongPass123!')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_injection(self):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; echo INJECTED', 'os': 'linux'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'INJECTED')

    def test_cmd_lab3_accepts_normal_hostname(self):
        response = self.client.post('/cmd_lab3', {'domain': 'localhost', 'os': 'linux'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Output')
