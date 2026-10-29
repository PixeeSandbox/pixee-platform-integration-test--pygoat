from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="testpassword123",
        )

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain_without_calling_subprocess(self, mock_run):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com;id", "os": "win"},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid hostname")
        mock_run.assert_not_called()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self, mock_run):
        mock_run.return_value = Mock(stdout="lookup ok", stderr="")
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
            text=True,
        )
