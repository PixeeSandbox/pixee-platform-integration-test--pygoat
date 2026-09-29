from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="cmduser", password="StrongPass123!")

    def setUp(self):
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_unsafe_domain_before_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
