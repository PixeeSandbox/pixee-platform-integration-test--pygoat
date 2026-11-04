from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="testpass123",
        )
        self.client.force_login(self.user)

    def test_rejects_malicious_domain_input(self):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com;whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
