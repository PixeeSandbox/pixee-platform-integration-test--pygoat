from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_accepts_url_input_and_calls_safe_argument_vector(self, mock_run):
        mock_run.return_value = type("Result", (), {"stdout": "lookup ok", "stderr": ""})()

        response = self.client.post(
            reverse("Command Injection Lab"),
            {
                "domain": " https://www.Example.com ",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_invalid_domain(self, mock_run):
        response = self.client.post(
            reverse("Command Injection Lab"),
            {
                "domain": "example.com; rm -rf /",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
