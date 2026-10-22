from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, mock_run):
        mock_run.return_value.stdout = b"lookup output"
        mock_run.return_value.stderr = b""

        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell"))

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_without_subprocess(self, mock_run):
        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "example.com;id", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()
