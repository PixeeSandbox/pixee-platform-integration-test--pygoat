from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username="cmduser", password="StrongPass123!")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain_input(self):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain. Please submit a valid hostname.")
