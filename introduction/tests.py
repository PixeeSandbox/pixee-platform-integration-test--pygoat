from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters(self):
        User = get_user_model()
        user = User.objects.create_user(username="tester", password="password123")
        self.client.force_login(user)

        response = self.client.post("/cmd_lab", {"domain": "google.com; id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "uid=")
