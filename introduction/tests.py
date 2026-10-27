from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmdlabuser", password="password123")
        self.assertTrue(self.client.login(username="cmdlabuser", password="password123"))

    @patch("introduction.views.subprocess.run")
    def test_malicious_domain_is_rejected_without_subprocess_call(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")

    @patch("introduction.views.subprocess.run")
    def test_valid_domain_uses_argument_vector(self, mock_run):
        process = Mock()
        process.stdout = b"resolved\n"
        process.stderr = b""
        mock_run.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com ", "os": "linux"},
        )

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertContains(response, "resolved")
