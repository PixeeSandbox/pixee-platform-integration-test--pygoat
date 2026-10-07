from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(user)

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;echo injected_marker", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "injected_marker")
