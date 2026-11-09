from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='test-password-123',
        )

    @patch('introduction.other_views.render', return_value=HttpResponse('rendered'))
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self, mock_run, mock_render):
        mock_run.return_value = Mock(stdout='lookup output', stderr='')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(response.content, b'rendered')
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'lookup output')

    @patch('introduction.other_views.render', return_value=HttpResponse('blocked'))
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_hostname_without_running_command(self, mock_run, mock_render):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertEqual(response.content, b'blocked')
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Something went wrong')
