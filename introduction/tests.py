from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdtester',
            password='StrongPass123!'
        )

    def test_cmd_lab3_rejects_malicious_domain(self):
        self.assertTrue(self.client.login(username='cmdtester', password='StrongPass123!'))

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com;id',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
