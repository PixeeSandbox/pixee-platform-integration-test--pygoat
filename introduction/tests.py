from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="cmdlab-user",
            password="password123",
        )
        cls.factory = RequestFactory()

    def _build_request(self, domain, os_name):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": domain, "os": os_name},
        )
        request.user = self.user
        return request

    def test_cmd_lab_uses_safe_argv_for_valid_domain(self):
        request = self._build_request("example.com", "win")
        mock_result = Mock(stdout="resolved output", stderr="")

        with patch("introduction.views.subprocess.run", return_value=mock_result) as mock_run:
            response = cmd_lab(request)

        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved output")

    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self):
        request = self._build_request("example.com;id", "linux")

        with patch("introduction.views.subprocess.run") as mock_run:
            response = cmd_lab(request)

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
