from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
