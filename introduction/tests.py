from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'linux'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
