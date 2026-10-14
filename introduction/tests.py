from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmduser", password="password123"
        )

    def test_cmd_lab_rejects_command_injection_payload(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com;whoami", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain provided")
