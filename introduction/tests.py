from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import views


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username="tester", password="password")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = Mock(stdout="resolved\n", stderr="")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertEqual(mock_run.call_args.kwargs, {"capture_output": True, "text": True})
        self.assertContains(response, "resolved")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_run):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")
