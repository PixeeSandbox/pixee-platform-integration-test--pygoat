from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_cmd_lab_rejects_malicious_domain_input(self):
        self.client.force_login(self.user)

        response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
