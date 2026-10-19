from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmduser", password="Passw0rd123")
        self.client.force_login(self.user)

    def _post_invalid_domain(self, domain):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post("/cmd_lab", {"domain": domain, "os": "linux"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    def test_cmd_lab_rejects_shell_separator_domain(self):
        self._post_invalid_domain("example.com; id")

    def test_cmd_lab_rejects_whitespace_domain(self):
        self._post_invalid_domain("example.com whoami")
