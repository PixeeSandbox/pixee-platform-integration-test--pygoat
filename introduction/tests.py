from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"example output", b"")
        mock_popen.return_value = process

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs["shell"])
        context = response.context[0] if isinstance(response.context, list) else response.context
        self.assertEqual(context["output"], "example output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        context = response.context[0] if isinstance(response.context, list) else response.context
        self.assertEqual(context["output"], "Invalid domain")
