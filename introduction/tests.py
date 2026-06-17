from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab_rejects_invalid_domain_without_running_command(self):
        request = self.factory.post("/cmd_lab", {"domain": ";id", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch("introduction.views.subprocess.Popen") as popen_mock:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Something went wrong", response.content)
        popen_mock.assert_not_called()

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        process = MagicMock()
        process.communicate.return_value = ("lookup ok", "")

        with patch("introduction.views.subprocess.Popen", return_value=process) as popen_mock:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"lookup ok", response.content)
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell"))
        self.assertTrue(kwargs.get("text"))
