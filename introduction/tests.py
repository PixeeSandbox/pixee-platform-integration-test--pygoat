from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmd-user",
            password="secure-password123",
        )
        self.url = "/cmd_lab"

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_invokes_resolver_with_argument_list(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"resolver output", b"")
        mock_popen.return_value = process

        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertContains(response, "resolver output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_executing_command(self, mock_popen):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {"domain": "example.com; id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertContains(response, "Something went wrong")
