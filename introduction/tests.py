from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLabValidationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="cmduser", password="StrongPass123!")
        self.assertTrue(self.client.login(username="cmduser", password="StrongPass123!"))

    def test_cmd_lab_rejects_malicious_domain(self):
        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "https://www.example.com;id",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid domain", response.content.decode())
