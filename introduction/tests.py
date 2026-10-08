from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_cmd_lab_rejects_malicious_domain(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; echo pwned", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "pwned")
