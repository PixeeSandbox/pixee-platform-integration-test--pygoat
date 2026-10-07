from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def test_malicious_domain_is_rejected(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="cmdlabuser", password="password123")
        self.client.force_login(user)

        with patch("introduction.other_views.subprocess.run") as mock_run:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; echo pwned", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()
