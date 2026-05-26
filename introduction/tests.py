from types import SimpleNamespace
from unittest.mock import ANY, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import _normalize_cmd_lab_domain, cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def test_normalize_cmd_lab_domain_accepts_common_inputs(self):
        self.assertEqual(_normalize_cmd_lab_domain("https://www.Example.com/"), "Example.com")
        self.assertEqual(_normalize_cmd_lab_domain("example.com"), "example.com")

    def test_cmd_lab_rejects_invalid_domain_before_subprocess(self):
        request = self.factory.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "linux"})
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as popen_mock, patch("introduction.views.render", return_value=HttpResponse("ok")) as render_mock:
            cmd_lab(request)

        popen_mock.assert_not_called()
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2]["output"], "Invalid domain")

    def test_cmd_lab_uses_fixed_argument_list(self):
        request = self.factory.post("/cmd_lab", {"domain": "https://www.example.com/", "os": "win"})
        request.user = self.user

        process = SimpleNamespace(
            communicate=lambda: (b"stdout", b"stderr"),
        )

        with patch("introduction.views.subprocess.Popen", return_value=process) as popen_mock, patch("introduction.views.render", return_value=HttpResponse("ok")):
            cmd_lab(request)

        popen_mock.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )

    def test_cmd_lab_uses_dig_for_non_windows(self):
        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "linux"})
        request.user = self.user

        process = SimpleNamespace(
            communicate=lambda: (b"stdout", b"stderr"),
        )

        with patch("introduction.views.subprocess.Popen", return_value=process) as popen_mock, patch("introduction.views.render", return_value=HttpResponse("ok")):
            cmd_lab(request)

        popen_mock.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
