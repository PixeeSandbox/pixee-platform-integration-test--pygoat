from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_valid_hostname_uses_fixed_lookup_command(self):
        for os_value, executable in (("win", "nslookup"), ("linux", "dig")):
            with self.subTest(os=os_value), patch("introduction.views.subprocess.Popen") as popen:
                process = popen.return_value
                process.communicate.return_value = (b"lookup output", b"")
                request = self.request_factory.post(
                    "/cmd-lab/",
                    {"domain": "https://www.example.com", "os": os_value},
                )
                request.user = SimpleNamespace(is_authenticated=True)

                response = views.cmd_lab(request)

                self.assertEqual(response.status_code, 200)
                popen.assert_called_once_with(
                    [executable, "example.com"],
                    shell=False,
                    stdout=views.subprocess.PIPE,
                    stderr=views.subprocess.PIPE,
                )

    def test_invalid_hostname_is_rejected_without_subprocess(self):
        request = self.request_factory.post(
            "/cmd-lab/", {"domain": "example.com; whoami", "os": "linux"}
        )
        request.user = SimpleNamespace(is_authenticated=True)

        with patch("introduction.views.subprocess.Popen") as popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        popen.assert_not_called()
