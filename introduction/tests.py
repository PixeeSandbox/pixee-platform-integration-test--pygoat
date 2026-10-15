from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.username = "cmdlab3user"
        self.password = "StrongPassword123!"
        self.user = self.User.objects.create_user(username=self.username, password=self.password)

    def test_malicious_domain_is_rejected(self):
        self.client.force_login(self.user)
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com;whoami", "os": "linux"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_unauthenticated_request_redirects_to_login(self):
        response = self.client.get("/cmd_lab3")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)
