from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="password123")

    def _authenticated_post(self, data):
        request = self.factory.post("/cmd_lab", data=data)
        request.user = self.user
        return request

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self._authenticated_post(
            {"domain": "example.com; rm -rf /", "os": "win"}
        )

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process
        request = self._authenticated_post({"domain": "example.com", "os": "win"})

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        command, = mock_popen.call_args.args
        self.assertEqual(command, ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
