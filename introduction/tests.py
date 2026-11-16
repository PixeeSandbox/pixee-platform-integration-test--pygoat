from django.test import TestCase
from django.contrib.auth.models import User


class CmdLabCommandInjectionTest(TestCase):
    def test_rejects_domain_with_shell_metacharacters(self):
        user = User.objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; echo injected',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context['output'], 'Invalid domain')
        self.assertNotContains(response, 'injected')
