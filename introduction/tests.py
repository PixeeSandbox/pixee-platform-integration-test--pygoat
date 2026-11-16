import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction import views


User = get_user_model()


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="testpass123")

    def _post_request(self, data):
        request = self.factory.post("/cmd_lab", data=data)
        request.user = self.user
        return request

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_invalid_domain_without_running_subprocess(self, mock_popen):
        request = self._post_request({"domain": "example.com; rm -rf /", "os": "win"})

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_invokes_subprocess_without_shell_for_valid_domain(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"resolved\n", b"")
        mock_popen.return_value = process
        request = self._post_request({"domain": "https://www.example.com ", "os": "win"})

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
