from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmdlabuser", password="StrongPass123!")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value.stdout = "lookup ok\n"
        mock_run.return_value.stderr = ""

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True, check=False)
        self.assertContains(response, "lookup ok")
