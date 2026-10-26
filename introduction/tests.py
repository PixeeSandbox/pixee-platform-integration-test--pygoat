from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain_input(self):
        user = get_user_model().objects.create_user(username="testuser", password="password123")
        self.client.force_login(user)

        response = self.client.post("/cmd_lab", {"domain": "example.com;whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
