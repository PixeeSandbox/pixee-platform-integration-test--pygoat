from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3CommandInjectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmdlab3user", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_command_injection_payload(self):
        response = self.client.post("/cmd_lab3", {"domain": "example.com;id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
