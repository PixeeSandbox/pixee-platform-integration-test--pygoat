import subprocess
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="cmdlabuser",
            password="strong-password",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_list_based_subprocess_invocation(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com; echo vulnerable", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com; echo vulnerable"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
