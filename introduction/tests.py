from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_calling_subprocess(self, mock_popen):
        user = self.User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_login(user)

        response = self.client.post(
            "/cmd_lab3",
            data={"domain": "example.com; rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_execution_for_valid_domain(self, mock_popen):
        user = self.User.objects.create_user(username="testuser2", password="testpass123")
        self.client.force_login(user)
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"ok", b"")

        response = self.client.post(
            "/cmd_lab3",
            data={"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], -1)
        self.assertEqual(kwargs["stderr"], -1)
        self.assertContains(response, "ok")
