import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab_uses_structured_arguments_for_valid_domain(self):
        request = self.factory.post("/cmd_lab/", {"domain": "example.com", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"resolved", b"")

            response = cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertEqual(response.status_code, 200)

    def test_cmd_lab_rejects_injected_domain_without_invoking_subprocess(self):
        request = self.factory.post("/cmd_lab/", {"domain": "example.com; whoami", "os": "linux"})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
