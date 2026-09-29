from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmdlabuser", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters_in_domain(self):
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; whoami", "os": "linux"},
        )
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "whoami")
