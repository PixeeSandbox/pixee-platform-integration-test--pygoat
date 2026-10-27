from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        logged_in = self.client.login(username=user.username, password='testpass123')
        self.assertTrue(logged_in)

        response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'uid=')
