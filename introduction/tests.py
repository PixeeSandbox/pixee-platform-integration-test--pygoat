from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        user = get_user_model().objects.create_user(username="testuser", password="password123")
        request = RequestFactory().post("/cmd_lab3/", {"domain": "example.com;id", "os": "win"})
        request.user = user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode())
