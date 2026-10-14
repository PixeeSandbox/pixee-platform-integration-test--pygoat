from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, popen_mock):
        process_mock = popen_mock.return_value
        process_mock.communicate.return_value = (b"ok", b"")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, popen_mock):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com;whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 400)
        popen_mock.assert_not_called()
