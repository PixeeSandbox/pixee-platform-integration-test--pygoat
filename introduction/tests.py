from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain(self):
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_login(user)

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "whoami")
