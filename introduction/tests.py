from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction import views
from introduction.views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    def test_cmd_lab_rejects_malicious_domain_without_invoking_popen(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com;id", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_with_shell_disabled(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
