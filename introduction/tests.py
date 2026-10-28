from django.test import TestCase, Client
from django.contrib.auth.models import User


class CommandInjectionTests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        user = User.objects.create_user(username='cmduser', password='StrongPassword123!')
        client = Client()
        self.assertTrue(client.login(username='cmduser', password='StrongPassword123!'))

        response = client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'uid=')
