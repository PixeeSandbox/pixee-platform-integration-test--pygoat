from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLabTests(TestCase):
    def test_rejects_malicious_domain_input(self):
        user = get_user_model().objects.create_user(
            username="tester",
            password="StrongPass123!",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
