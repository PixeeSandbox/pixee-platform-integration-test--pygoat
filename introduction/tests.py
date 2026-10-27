from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            mock_popen.return_value.communicate.return_value = (b"ok", b"")

            response = cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertContains(response, "ok")

    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
