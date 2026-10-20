from django.test import TestCase, Client
from django.contrib.auth import get_user_model


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='cmdlab3user', password='StrongPass123!')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain(self):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
