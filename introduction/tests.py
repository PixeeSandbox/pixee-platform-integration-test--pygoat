from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, popen_mock, render_mock):
        process_mock = SimpleNamespace()
        process_mock.communicate = lambda: (b"valid-output", b"")
        popen_mock.return_value = process_mock
        render_mock.return_value = SimpleNamespace()

        request = self.factory.post("/cmd_lab3", {"domain": "example.com", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response, render_mock.return_value)
        popen_mock.assert_called_once()
        self.assertEqual(popen_mock.call_args.args[0], ["nslookup", "example.com"])
        self.assertFalse(popen_mock.call_args.kwargs.get("shell", False))

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_injected_domain(self, popen_mock, render_mock):
        render_mock.return_value = SimpleNamespace()

        request = self.factory.post("/cmd_lab3", {"domain": "example.com; id", "os": "linux"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response, render_mock.return_value)
        popen_mock.assert_not_called()
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2]["output"], "Invalid domain")
