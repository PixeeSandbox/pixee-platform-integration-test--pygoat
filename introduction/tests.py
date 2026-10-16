from django.test import TestCase
from django.contrib.auth.models import User


class CmdLabSecurityTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain(self):
        user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; id',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
