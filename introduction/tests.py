from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_before_command_execution(self, mock_run):
        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com;rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        mock_run.assert_not_called()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argument_list_with_shell_disabled_for_valid_domain(self, mock_run):
        mock_run.return_value = type('Result', (), {'stdout': 'example output\n', 'stderr': '', 'returncode': 0})()
        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['dig', 'example.com'], shell=False, capture_output=True, text=True)
