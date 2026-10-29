from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        user = User.objects.create_user(username='tester', password='password123')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid domain input')
        self.assertContains(response, 'Invalid domain input')
