from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username="cmduser", password="password123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_accepts_valid_domain_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"Lookup ok", b"")

        request = self.factory.post("/cmd_lab", data={"domain": "https://www.example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Lookup ok", response.content.decode())
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post("/cmd_lab", data={"domain": "example.com; whoami", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid domain", response.content.decode())
        mock_popen.assert_not_called()
