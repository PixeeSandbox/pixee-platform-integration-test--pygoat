from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com;id", "os": "linux"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_for_safe_domain(self):
        process = patch("introduction.other_views.subprocess.Popen").start()
        self.addCleanup(patch.stopall)
        process.return_value.communicate.return_value = (b"OK", b"")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OK")
        process.assert_called_once_with(
            ["dig", "example.com"],
            stdout=ANY,
            stderr=ANY,
        )
