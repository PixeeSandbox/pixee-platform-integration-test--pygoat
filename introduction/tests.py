from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabCommandInjectionTests(TestCase):
    def test_rejects_malicious_domain(self):
        User = get_user_model()
        user = User.objects.create_user(username="cmduser", password="pass12345")
        self.client.force_login(user)

        response = self.client.post("/cmd_lab", {"domain": "example.com; id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
