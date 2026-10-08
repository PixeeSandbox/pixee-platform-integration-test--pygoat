from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Mock()
        self.user.is_authenticated = True

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, popen_mock):
        request = self.factory.post("/cmd_lab", {"domain": "example.com;id", "os": "linux"})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid domain", response.content)
        popen_mock.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, popen_mock):
        process = Mock()
        process.communicate.return_value = (b"example.com\n", b"")
        popen_mock.return_value = process

        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "linux"})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertIn(b"example.com", response.content)
