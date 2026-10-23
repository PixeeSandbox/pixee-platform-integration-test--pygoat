from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_metacharacters_in_domain(self):
        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "uid=")
