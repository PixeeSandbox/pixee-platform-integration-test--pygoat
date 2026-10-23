import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        with patch("introduction.views.subprocess.Popen") as popen_mock:
            response = self.client.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "linux"})

        popen_mock.assert_not_called()
        self.assertContains(response, "Something went wrong")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_vector_for_valid_domain(self, popen_mock):
        process_mock = popen_mock.return_value
        process_mock.communicate.return_value = (b"lookup ok", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        popen_mock.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup ok")
