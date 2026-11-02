from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPassword123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"safe output", b"")
        mock_popen.return_value = process

        malicious_domain = "example.com; echo vulnerable"
        response = self.client.post(
            "/cmd_lab",
            {"domain": malicious_domain, "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", malicious_domain])
        self.assertFalse(kwargs.get("shell"))
