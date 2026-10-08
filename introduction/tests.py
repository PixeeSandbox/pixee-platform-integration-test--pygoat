from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="safe-password",
        )
        self.assertTrue(self.client.login(username="cmduser", password="safe-password"))

    def test_cmd_lab_rejects_shell_metacharacters(self):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; echo INJECTED", "os": "linux"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "INJECTED")
