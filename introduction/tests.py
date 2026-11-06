from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="cmduser", password="password123")

    def test_cmd_lab_rejects_shell_metacharacters(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "uid=")
