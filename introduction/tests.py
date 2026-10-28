from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list(self, mock_run, mock_render):
        mock_run.return_value = SimpleNamespace(returncode=0, stdout="lookup ok", stderr="")
        mock_render.return_value = "rendered"
        request = self.factory.post("/cmd_lab", {"domain": "https://www.example.com", "os": "linux"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response, "rendered")
        self.assertEqual(mock_run.call_args.args[0], ["dig", "example.com"])
        self.assertNotIn("shell", mock_run.call_args.kwargs)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_run, mock_render):
        mock_render.return_value = "rendered"
        request = self.factory.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "linux"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response, "rendered")
        mock_run.assert_not_called()
        self.assertEqual(mock_render.call_args.args[2]["output"], "Something went wrong")
