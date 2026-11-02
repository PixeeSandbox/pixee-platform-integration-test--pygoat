from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_get_renders_for_authenticated_user(self):
        response = self.client.get("/cmd_lab")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Name Server Lookup")

    def test_cmd_lab_rejects_malicious_domain_input(self):
        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "example.com;id",
                "os": "win",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "example.com;id")
