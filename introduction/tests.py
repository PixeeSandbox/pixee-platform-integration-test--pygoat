from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_invalid_domain_and_uses_argument_list_for_valid_domain(self, mock_popen):
        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {"domain": "example.com;whoami", "os": "linux"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Invalid domain")
        mock_popen.assert_not_called()

        process = Mock()
        process.communicate.return_value = (b"valid response", b"")
        mock_popen.return_value = process

        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {"domain": "example.com", "os": "win"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "valid response")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
