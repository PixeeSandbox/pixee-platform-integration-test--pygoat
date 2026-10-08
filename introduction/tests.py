from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="safe-password",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_injection_in_domain(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {
                "domain": "https://www.example.com; cat /etc/passwd",
                "os": "linux",
            },
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode())
        mock_popen.assert_not_called()
