from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="password123")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        self.assertTrue(self.client.login(username="cmduser", password="password123"))

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        self.assertTrue(self.client.login(username="cmduser", password="password123"))

        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
