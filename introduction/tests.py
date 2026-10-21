from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass12345")

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        self.assertTrue(self.client.login(username="testuser", password="pass12345"))
        response = self.client.post("/cmd_lab3", {"domain": "example.com; id", "os": "win"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertNotContains(response, "uid=")
