from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser",
            password="Password123!",
        )

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        logged_in = self.client.login(username="testuser", password="Password123!")
        self.assertTrue(logged_in)

        response = self.client.post(
            "/cmd_lab3",
            {
                "domain": "example.com;whoami",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain supplied")
