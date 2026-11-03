from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters(self):
        user = User.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(user)

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; echo injected", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "injected")
