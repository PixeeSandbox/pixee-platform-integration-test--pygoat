from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser",
            password="password123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain(self):
        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "https://www.example.com; whoami",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertEqual(response.context["output"], "Invalid domain")
