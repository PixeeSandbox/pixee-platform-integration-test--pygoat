from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="pass12345",
        )
        self.assertTrue(self.client.login(username="cmduser", password="pass12345"))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "example.com; touch /tmp/pwned",
                "os": "win",
            },
        )

        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
