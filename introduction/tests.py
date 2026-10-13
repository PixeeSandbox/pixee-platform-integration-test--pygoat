from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import ANY, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.login(username="tester", password="password123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_invocation_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        for domain in ["example.com", "example.com; whoami"]:
            with self.subTest(domain=domain):
                response = self.client.post("/cmd_lab", {"domain": domain, "os": "win"})
                self.assertEqual(response.status_code, 200)
                mock_popen.assert_called_with(
                    ["nslookup", domain.replace("https://www.", "")],
                    stdout=ANY,
                    stderr=ANY,
                )
                self.assertNotIn("shell", mock_popen.call_args.kwargs)
                mock_popen.reset_mock()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_renders_output_for_normal_request(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=ANY,
            stderr=ANY,
        )
