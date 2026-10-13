from django.test import TestCase
from django.contrib.auth import get_user_model


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="Testpass123!",
        )

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com;whoami", "os": "win"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertNotContains(response, "whoami")
