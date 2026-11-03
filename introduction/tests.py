from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabCommandInjectionRegressionTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmdlabuser", password="safe-password-123")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters_in_domain(self):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; echo hacked", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertNotIn("hacked", content)
        self.assertIn("Something went wrong", content)
