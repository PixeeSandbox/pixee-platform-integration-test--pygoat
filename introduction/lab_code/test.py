from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="cmdpass123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        with patch("introduction.views.subprocess.Popen") as mocked_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com;id", "os": "linux"},
            )
        mocked_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")

    def test_cmd_lab_rejects_option_like_prefix(self):
        with patch("introduction.views.subprocess.Popen") as mocked_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "-example.com", "os": "win"},
            )
        mocked_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")
