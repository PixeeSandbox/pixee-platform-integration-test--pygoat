from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='testuser', password='testpass123')
        self.assertTrue(self.client.login(username='testuser', password='testpass123'))

    def test_cmd_lab3_rejects_malicious_domain(self):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; echo injected',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
