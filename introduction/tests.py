from django.test import TestCase
from django.contrib.auth.models import User


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'linux'})
        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid domain', content)
        self.assertNotIn('uid=', content)
