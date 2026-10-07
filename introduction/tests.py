from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab3', {'domain': 'example.com;echo INJECTED', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'INJECTED')
