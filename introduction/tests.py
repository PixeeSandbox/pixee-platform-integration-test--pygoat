from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="cmd_lab_user",
            password="TestPass123!",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain_payload(self):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;id", "os": "win"},
        )
        self.assertContains(response, "Something went wrong")

    def test_cmd_lab_redirects_unauthenticated_users(self):
        client = Client()
        response = client.get("/cmd_lab")
        self.assertEqual(response.status_code, 302)
