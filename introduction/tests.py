from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username="tester", password="secret")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_invokes_subprocess_safely(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"resolved", b"")
        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertIn("resolved", response.content.decode("utf-8"))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "win"})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn("Invalid domain", response.content.decode("utf-8"))
