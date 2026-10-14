from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, Mock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="password123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_argument_list_for_valid_domains(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        for os_value, expected_command in (("win", ["nslookup", "example.com"]), ("linux", ["dig", "example.com"])):
            with self.subTest(os=os_value):
                request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": os_value})
                request.user = self.user

                response = cmd_lab(request)

                self.assertEqual(response.status_code, 200)
                self.assertIn("lookup ok", response.content.decode())
                mock_popen.assert_called_with(
                    expected_command,
                    shell=False,
                    stdout=ANY,
                    stderr=ANY,
                )
                mock_popen.reset_mock()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        request = self.factory.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "linux"})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid domain", response.content.decode())
        mock_popen.assert_not_called()
