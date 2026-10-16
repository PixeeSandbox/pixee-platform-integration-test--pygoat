from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmd_lab3_user", password="StrongPass123!")
        self.client = Client()
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_injection_payload(self):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; id", "os": "linux"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain input")
