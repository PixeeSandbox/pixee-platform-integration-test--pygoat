from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='cmdlab3user', password='testpassword123')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; echo hacked',
            'os': 'linux',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
