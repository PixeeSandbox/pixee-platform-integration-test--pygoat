from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdtester",
            password="password123",
        )

    def test_cmd_lab_rejects_malicious_domain_without_calling_popen(self):
        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "https://www.example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_and_disables_shell(self):
        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "https://www.example.com", "os": "linux"},
        )
        request.user = self.user

        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"lookup ok", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process_mock) as mock_popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        process_mock.communicate.assert_called_once()
