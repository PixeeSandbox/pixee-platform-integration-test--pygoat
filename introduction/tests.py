from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_invalid_domain_input(self):
        user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='TestPass123!',
        )
        self.client.force_login(user)

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com;id',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
