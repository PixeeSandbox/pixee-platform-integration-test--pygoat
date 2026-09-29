from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_run):
        mock_run.return_value = MagicMock(stdout='example output\n', stderr='')
        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True, check=False)
        self.assertEqual(response.status_code, 200)
        self.assertIn('example output', response.content.decode())

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_run):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid domain', response.content.decode())
