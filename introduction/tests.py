from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_rejects_domain_with_shell_syntax(self):
        user = User.objects.create_user(username='cmd-test', password='password')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; whoami',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid domain')
