from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="password")

    def test_cmd_lab_rejects_malicious_domain_without_running_subprocess(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode())
        mock_popen.assert_not_called()
