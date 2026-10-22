from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="password123")

    def test_cmd_lab3_rejects_malicious_domain_before_popen(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode("utf-8"))
        mock_popen.assert_not_called()
