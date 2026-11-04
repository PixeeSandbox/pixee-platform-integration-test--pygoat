from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3RegressionTests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.assertTrue(self.client.login(username='testuser', password='testpass123'))

        malicious_domain = 'example.com;echo PWNED'
        response = self.client.post('/cmd_lab3', {'domain': malicious_domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'PWNED')
