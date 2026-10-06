from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="testuser", password="StrongPass123!")
        self.client.login(username="testuser", password="StrongPass123!")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com; echo injected-output", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotIn(b"injected-output", response.content)
        mock_run.assert_not_called()
