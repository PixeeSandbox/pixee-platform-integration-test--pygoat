from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com;echo INJECTED',
            'os': 'win',
        })

        self.assertNotContains(response, 'INJECTED')
