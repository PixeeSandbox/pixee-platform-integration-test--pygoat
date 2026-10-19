from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_shell_execution(self, mock_popen):
        payload = "example.com; cat /etc/passwd"
        request = self.factory.post(
            "/cmd_lab",
            {"domain": f"https://www.{payload}", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, payload)
