from django.test import TestCase
from django.contrib.auth import get_user_model


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

    def test_cmd_lab_rejects_shell_metacharacters(self):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
