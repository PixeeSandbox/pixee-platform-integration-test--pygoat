from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )

    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab_uses_argument_list_without_shell(self):
        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"lookup ok", b"")

            response = cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(response.status_code, 200)

    def test_cmd_lab_rejects_malicious_domain_without_invoking_command(self):
        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
