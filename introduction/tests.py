from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser", password="password123"
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_normalizes_valid_domain_and_uses_argument_list(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"ok", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com/path/", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "ok")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell"))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injection_payload(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
        mock_popen.assert_not_called()
