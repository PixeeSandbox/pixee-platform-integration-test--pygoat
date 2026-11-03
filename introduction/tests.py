from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_valid_hostname_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"sample output", b"")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "sample output")
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_injected_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
        mock_popen.assert_not_called()
