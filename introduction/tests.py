from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )

    def test_cmd_lab_rejects_shell_injection_payload(self):
        self.client.login(username="cmdlabuser", password="StrongPass123!")
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertNotContains(response, "whoami")
