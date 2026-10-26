from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="secure-pass123")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com; whoami && `id`", "os": "win"},
            )

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
