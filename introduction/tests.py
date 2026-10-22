from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabValidationTestCase(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmduser", password="Password123!")
        self.client.login(username="cmduser", password="Password123!")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; whoami && `id`", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain provided.")
        self.assertNotContains(response, "uid=")
        self.assertNotContains(response, "whoami")
        mock_popen.assert_not_called()
