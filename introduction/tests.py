import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="testpassword123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab/",
            {
                "domain": "https://www.example.com; rm -rf /",
                "os": "linux",
            },
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn("Something went wrong", response.content.decode())

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        request = self.factory.post(
            "/cmd_lab/",
            {
                "domain": "https://www.example.com",
                "os": "linux",
            },
        )
        request.user = self.user

        response = cmd_lab(request)

        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ["dig", "example.com"])
        self.assertNotIn("shell", called_kwargs)
        self.assertEqual(called_kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(called_kwargs["stderr"], subprocess.PIPE)
        self.assertIn("lookup ok", response.content.decode())
