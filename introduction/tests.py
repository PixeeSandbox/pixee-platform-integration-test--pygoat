from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="cmduser",
            password="password123",
        )
        self.assertTrue(self.client.login(username="cmduser", password="password123"))

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain(self, mocked_run):
        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "example.com; echo pwned",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "pwned")
        mocked_run.assert_not_called()
