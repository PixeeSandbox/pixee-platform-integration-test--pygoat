from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="cmd_tester")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters_in_domain(self):
        response = self.client.post("/cmd_lab", {"domain": "example.com;id", "os": "win"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid input")
