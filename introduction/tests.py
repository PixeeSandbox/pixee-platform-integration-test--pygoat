from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdtester",
            password="secure-pass-123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"example output", b"")

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "example output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_executing_command(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
