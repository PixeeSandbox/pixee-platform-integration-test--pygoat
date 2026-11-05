from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="cmdlabuser", password="StrongPass123!")
        self.client.force_login(user)

        response = self.client.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
