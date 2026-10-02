from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_rejects_malicious_domain_without_running_command(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse('rendered')
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'rendered')
        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Invalid domain')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_valid_domain_uses_argument_list(self, mock_run, mock_render):
        mock_run.return_value.stdout = 'lookup output'
        mock_run.return_value.stderr = ''
        mock_render.return_value = HttpResponse('rendered')
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'rendered')
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True)
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'lookup output')
