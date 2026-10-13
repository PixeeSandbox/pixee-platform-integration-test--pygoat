from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        payload = 'example.com; echo injected'
        response = self.client.post('/cmd_lab3', {
            'domain': payload,
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        self.assertNotContains(response, payload)
        self.assertNotContains(response, 'injected')
