from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings


@override_settings(ALLOWED_HOSTS=["testserver"])
class CmdLab3SecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="cmdlab3-user", password="password123")

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com;whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "whoami")
