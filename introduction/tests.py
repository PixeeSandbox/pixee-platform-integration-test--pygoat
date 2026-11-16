import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="testpass123",
        )

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_hostname(self, mock_run):
        request = self.factory.post(
            "/cmd_lab/",
            {
                "domain": "example.com; rm -rf /",
                "os": "win",
            },
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, mock_run):
        mock_run.return_value = Mock(stdout=b"lookup ok", stderr=b"")
        request = self.factory.post(
            "/cmd_lab/",
            {
                "domain": "https://www.example.com",
                "os": "win",
            },
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup ok")
