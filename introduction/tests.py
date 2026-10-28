from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="password123",
        )

    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab3_uses_safe_subprocess_arguments(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"lookup ok", b"")

            response = cmd_lab3(request)

        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_popen.call_args[0][0], ["nslookup", "example.com"])
        self.assertIn(b"lookup ok", response.content)

    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertIn(b"Something went wrong", response.content)
