from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword123",
        )

    def test_cmd_lab3_rejects_malicious_domain_without_running_subprocess(self):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argv_list_without_shell_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        mock_process = Mock()
        mock_process.communicate.return_value = (b"lookup output", b"")

        with patch("introduction.other_views.subprocess.Popen", return_value=mock_process) as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertContains(response, "lookup output")
