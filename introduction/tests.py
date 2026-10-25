from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters_in_domain(self):
        User = get_user_model()
        User.objects.create_user(username="testuser", password="StrongPass123!")
        self.assertTrue(self.client.login(username="testuser", password="StrongPass123!"))

        response = self.client.post(
            "/cmd_lab3",
            data={
                "domain": "example.com; echo injected",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
