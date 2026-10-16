from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="password123")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_safe_argument_list_for_valid_hostname(self, mock_run):
        mock_run.return_value = SimpleNamespace(stdout="lookup ok", stderr="")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertNotIn("shell", mock_run.call_args.kwargs)
        self.assertContains(response, "lookup ok")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; id", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")
