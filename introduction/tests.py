from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def test_cmd_lab_rejects_command_injection_payload(self):
        user = User.objects.create_user(username='cmdlabuser', password='password123')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; id',
            'os': 'win',
        })

        self.assertNotContains(response, 'uid=')
