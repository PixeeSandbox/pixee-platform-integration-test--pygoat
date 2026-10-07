from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmduser", password="StrongPass123!")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_injected_domain(self):
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid domain", response.content)
