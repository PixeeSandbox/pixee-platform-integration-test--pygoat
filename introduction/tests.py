from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters_in_domain(self):
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_login(user)

        response = self.client.post(reverse("Command Injection Lab 3"), {
            "domain": "example.com; id",
            "os": "linux",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
