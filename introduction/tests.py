from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="strong-password",
        )

    def test_cmd_lab_uses_argv_execution_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "lookup ok"
            mock_run.return_value.stderr = ""

            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args.args[0], ["nslookup", "example.com"])
        self.assertNotIsInstance(mock_run.call_args.args[0], str)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; id", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.run") as mock_run:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()
