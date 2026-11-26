from django.test import TestCase
from django.contrib.auth.models import User


class CommandInjectionValidationTests(TestCase):
    def test_cmd_lab3_rejects_shell_syntax_in_domain(self):
        user = User.objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(user)

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b"Invalid domain")
