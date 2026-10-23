from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from introduction.views import _build_lookup_command


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )

    def test_cmd_lab_rejects_malicious_domain(self):
        self.client.force_login(self.user)
        with patch("introduction.views.subprocess.Popen") as mocked_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com;whoami", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mocked_popen.assert_not_called()

    def test_build_lookup_command_validates_domain(self):
        self.assertEqual(
            _build_lookup_command("linux", "example.com"),
            ["dig", "example.com"],
        )
        self.assertEqual(
            _build_lookup_command("win", "https://www.example.com"),
            ["nslookup", "example.com"],
        )
        with self.assertRaises(ValueError):
            _build_lookup_command("linux", "-example.com")
