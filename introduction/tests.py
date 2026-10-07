from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_safe_domain(self, mock_run):
        mock_run.return_value = MagicMock(stdout="mocked stdout", stderr="mocked stderr")
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_run.call_args.args[0], ["dig", "example.com"])
        self.assertEqual(mock_run.call_args.kwargs, {"capture_output": True, "text": True, "check": False})
        self.assertContains(response, "mocked stdout")
        self.assertContains(response, "mocked stderr")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")
