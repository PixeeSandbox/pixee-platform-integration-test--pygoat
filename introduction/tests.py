from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, patch

from .views import cmd_lab


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="pass12345")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_domain_input(self, mock_popen):
        malicious_domain = "example.com; touch /tmp/pwned && whoami"
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"safe output", b"")

        request = self.factory.post(
            "/cmd_lab",
            {"domain": malicious_domain, "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", malicious_domain],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
