from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabRegressionTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="cmduser",
            password="secure-test-password123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        login_successful = self.client.login(
            username="cmduser",
            password="secure-test-password123",
        )
        self.assertTrue(login_successful)

        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "example.com; id",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
