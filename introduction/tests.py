from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmdtest', password='password123')
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain(self):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
