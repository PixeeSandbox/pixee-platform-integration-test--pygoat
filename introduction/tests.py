from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="StrongPass123!")
        self.client.login(username="cmduser", password="StrongPass123!")

    def test_rejects_command_injection_in_domain(self):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
