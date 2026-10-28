from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;id", "os": "linux"},
        )

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_argument_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"example output", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "linux"},
        )

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "example output")
