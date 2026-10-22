from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")

    def test_cmd_lab_uses_argument_list_with_shell_disabled(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "linux"},
        )
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as mock_popen:
            response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
