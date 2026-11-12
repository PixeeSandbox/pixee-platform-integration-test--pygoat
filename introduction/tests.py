from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd(self, domain, os="linux"):
        request = self.factory.post("/cmd_lab", {"domain": domain, "os": os})
        request.user = type("User", (), {"is_authenticated": True})()
        return cmd_lab(request)

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_hostname_with_command_metacharacters(self, mock_popen):
        response = self.post_cmd("example.com; whoami")

        self.assertContains(response, "Invalid hostname")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_valid_hostname_is_passed_as_argument_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup", b"")

        for os, executable in (("win", "nslookup"), ("linux", "dig")):
            with self.subTest(os=os):
                self.post_cmd("example.com", os)

                args, kwargs = mock_popen.call_args
                self.assertEqual(args[0], [executable, "example.com"])
                self.assertIs(kwargs["shell"], False)
                self.assertIn("stdout", kwargs)
                self.assertIn("stderr", kwargs)
                mock_popen.reset_mock()
