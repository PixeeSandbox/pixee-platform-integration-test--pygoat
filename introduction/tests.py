from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3ValidationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.login(username="testuser", password="testpass123")

    def test_rejects_malicious_domain(self):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain provided")
