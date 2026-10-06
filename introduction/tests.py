from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client.login(username="testuser", password="testpass123")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_safe_argument_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"resolved", b"")
        mock_popen.return_value = process
        mock_render.return_value = Mock(status_code=200)

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertTrue(response)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=-1,
            stderr=-1,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        mock_render.assert_called_once()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = Mock(status_code=200)

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertTrue(response)
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[1], "Lab/CMD/cmd_lab.html")
        self.assertEqual(mock_render.call_args.args[2], {"output": "Invalid domain"})
