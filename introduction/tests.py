from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="secureuser", password="pass12345")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_command_execution(self, mock_popen):
        logged_in = self.client.login(username="secureuser", password="pass12345")
        self.assertTrue(logged_in)

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
