from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmdlabuser", password="StrongPass123!")
        self.url = reverse("Command Injection Lab 3")

    def test_cmd_lab3_rejects_malicious_domain_without_running_subprocess(self):
        self.client.force_login(self.user)

        with patch("introduction.other_views.subprocess.run") as mock_run:
            response = self.client.post(
                self.url,
                {"domain": "example.com; rm -rf /", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()

    def test_cmd_lab3_runs_subprocess_with_argument_list_for_valid_domain(self):
        self.client.force_login(self.user)

        with patch("introduction.other_views.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "resolved output\n"
            mock_run.return_value.stderr = ""
            response = self.client.post(
                self.url,
                {"domain": "example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["nslookup", "example.com"], shell=False, capture_output=True, text=True)
        self.assertContains(response, "resolved output")
