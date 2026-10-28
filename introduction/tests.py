from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3CommandInjectionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmdtester", password="secure-password123")
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_injection_payload(self):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertNotContains(response, "example.com; id")
