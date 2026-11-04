from django.contrib.auth import get_user_model
from django.test import TestCase

from .views import is_valid_cmd_domain


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="strong-password123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[0]["output"], "Something went wrong")
        self.assertFalse(is_valid_cmd_domain("example.com;id"))

    def test_cmd_lab_allows_valid_hostname(self):
        self.assertTrue(is_valid_cmd_domain("example.com"))
