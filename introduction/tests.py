from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters_without_invoking_shell(self):
        user = get_user_model().objects.create_user(
            username="cmduser",
            password="StrongPassword123!",
        )
        self.client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                data={"domain": "example.com; rm -rf /", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
