import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "linux"},
        )
        request.user = self.user
        process = Mock()
        process.communicate.return_value = (b"DNS result\n", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ["dig", "example.com"])
        self.assertNotIn("shell", called_kwargs)
        self.assertEqual(called_kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(called_kwargs["stderr"], subprocess.PIPE)
        self.assertContains(response, "DNS result")
