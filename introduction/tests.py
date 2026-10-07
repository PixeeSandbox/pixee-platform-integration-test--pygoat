from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CommandInjectionRemediationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmd_user", password="strong-password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; cat /etc/passwd", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertNotContains(response, "cat /etc/passwd")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_accepts_benign_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"resolved", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ["dig", "example.com"])
        self.assertEqual(mock_popen.call_args.kwargs["shell"], False)
