import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabSecurityTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="password123")

    def test_cmd_lab_passes_argv_list_to_popen(self):
        malicious_domain = "example.com; touch /tmp/pwned && echo hacked"

        for os_value, expected_command in (("linux", ["dig", malicious_domain]), ("win", ["nslookup", malicious_domain])):
            with self.subTest(os=os_value):
                request = self.factory.post(
                    "/cmd_lab/",
                    {"domain": malicious_domain, "os": os_value},
                )
                request.user = self.user

                with patch("introduction.views.subprocess.Popen") as mock_popen:
                    process = mock_popen.return_value
                    process.communicate.return_value = (b"lookup output", b"")

                    response = cmd_lab(request)

                mock_popen.assert_called_once_with(
                    expected_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(response.status_code, 200)
