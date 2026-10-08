from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.password = "TestPass123!"
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password=self.password,
        )
        self.client.login(username=self.user.username, password=self.password)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_and_disables_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"mocked output", b"")
        mock_popen.return_value = process

        payload = "example.com; id"
        response = self.client.post("/cmd_lab", {"domain": payload, "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "mocked output")
        mock_popen.assert_called_once_with(
            ["dig", payload],
            shell=False,
            stdout=-1,
            stderr=-1,
        )
