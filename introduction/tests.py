from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CommandInjectionLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password12345",
        )
        self.url = reverse("Command Injection Lab 3")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_run):
        mock_run.return_value.stdout = "resolved output"
        mock_run.return_value.stderr = ""
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(response.context["output"], "resolved output")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"domain": "example.com;whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")
