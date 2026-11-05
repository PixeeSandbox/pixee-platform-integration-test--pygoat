from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_run):
        mock_run.return_value.stdout = 'example.com.  IN  A  1.2.3.4\n'
        mock_run.return_value.stderr = ''
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('example.com.  IN  A  1.2.3.4', response.content.decode())
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            capture_output=True,
            text=True
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_injected_domain(self, mock_run):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com;whoami', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        mock_run.assert_not_called()
