from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain(self):
        user = get_user_model().objects.create_user(username="cmduser", password="pass12345")
        self.client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "google.com && dir", "os": "linux"},
            )

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
