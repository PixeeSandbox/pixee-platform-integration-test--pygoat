from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters_without_injecting_output(self):
        User = get_user_model()
        user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(user)

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com; echo injected', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'injected')
