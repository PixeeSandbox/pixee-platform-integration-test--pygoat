from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; rm -rf /", "os": "linux"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
