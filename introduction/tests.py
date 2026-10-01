from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_shell_injection_in_domain(self):
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
