from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_cmd_lab_rejects_shell_metacharacters_in_domain(self):
        self.client.force_login(self.user)
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post("/cmd_lab", {"domain": "example.com;id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
