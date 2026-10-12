from django.test import TestCase
from django.contrib.auth import get_user_model


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="cmduser", password="password12345")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        response = self.client.post("/cmd_lab", {"domain": "example.com;whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
