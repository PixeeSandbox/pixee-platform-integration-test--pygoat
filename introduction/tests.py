import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )

    def setUp(self):
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_and_disables_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"stubbed stdout", b"stubbed stderr")

        malicious_domain = "example.com; touch /tmp/pwned"
        response = self.client.post(
            "/cmd_lab",
            {"domain": malicious_domain, "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", malicious_domain],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "stubbed stdout")
        self.assertContains(response, "stubbed stderr")
