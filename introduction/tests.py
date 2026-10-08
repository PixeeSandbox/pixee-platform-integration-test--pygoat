from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmd-user",
            password="secure-password",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_subprocess_arguments(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"example output", b"")

        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_execution(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Invalid domain", status_code=400)
        mock_popen.assert_not_called()
