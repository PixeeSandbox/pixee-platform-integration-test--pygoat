from unittest.mock import ANY, Mock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
        )

    def test_cmd_lab_rejects_malformed_domain_without_invoking_subprocess(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com;id", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as popen:
            response = cmd_lab(request)

        self.assertContains(response, "Invalid domain")
        popen.assert_not_called()

    def test_cmd_lab_uses_safe_argument_list_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "https://www.example.com.", "os": "linux"},
        )
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b"lookup output", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as popen:
            response = cmd_lab(request)

        popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertContains(response, "lookup output")
