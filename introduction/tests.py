from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class CommandInjectionLabTests(TestCase):
    def test_cmd_lab_rejects_shell_injection_in_domain(self):
        User = get_user_model()
        user = User.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(user)

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
