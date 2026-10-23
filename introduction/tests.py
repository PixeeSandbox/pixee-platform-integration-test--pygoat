from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "https://www.example.com;echo injected",
                "os": "linux",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "injected")
