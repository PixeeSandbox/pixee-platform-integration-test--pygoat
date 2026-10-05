from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_input(self):
        user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="testpass123",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {"domain": "google.com && id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
