from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain_without_invoking_shell(self):
        User = get_user_model()
        user = User.objects.create_user(username="tester", password="secure-password")
        self.client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com; touch /tmp/pwned", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
