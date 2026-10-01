from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="StrongPass123!")
        self.assertTrue(self.client.login(username="testuser", password="StrongPass123!"))

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        response = self.client.post(
            "/cmd_lab3",
            {
                "domain": "example.com; rm -rf /",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertNotContains(response, "example.com; rm -rf /")
