from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain(self):
        user = get_user_model().objects.create_user(username="cmduser", password="password123")
        self.client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as popen:
            response = self.client.post("/cmd_lab", {"domain": "example.com;id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid input")
        popen.assert_not_called()
