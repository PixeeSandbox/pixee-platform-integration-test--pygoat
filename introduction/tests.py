from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain(self):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com; echo pwned", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertNotContains(response, "pwned")
