from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        response = self.client.post(
            '/cmd_lab',
            {
                'domain': 'https://www.example.com; id',
                'os': 'linux',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        self.assertNotContains(response, 'Something went wrong')
