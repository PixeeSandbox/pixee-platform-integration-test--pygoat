from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import ANY, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cmd_lab_user",
            password="testpassword123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_vector_on_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        domain = "example.com; echo pwned"
        response = self.client.post("/cmd_lab", {"domain": domain, "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", domain],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_vector_on_non_windows(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        domain = "example.com; echo pwned"
        response = self.client.post("/cmd_lab", {"domain": domain, "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", domain],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
