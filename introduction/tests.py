from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_injected_domain_input(self):
        response = self.client.post("/cmd_lab3", {"domain": "example.com;id", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[0]["output"], "Invalid domain")
        self.assertNotIn("uid=", response.content.decode())
