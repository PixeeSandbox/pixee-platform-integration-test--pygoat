from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_input(self):
        User = get_user_model()
        user = User.objects.create_user(username="cmdtester", password="secure-password-123")
        client = Client()
        client.force_login(user)

        response = client.post("/cmd_lab3", {"domain": "example.com;id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lab/CMD/cmd_lab.html")
        self.assertContains(response, "Invalid domain")
