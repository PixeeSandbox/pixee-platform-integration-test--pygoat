import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injected_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('rendered')
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; rm -rf /',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Invalid domain')
        self.assertEqual(response.content, b'rendered')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen, mock_render):
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('lookup ok', '')
        mock_popen.return_value = mock_process
        mock_render.return_value = HttpResponse('rendered')
        request = self.factory.post('/cmd_lab3', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(mock_render.call_args[0][2]['output'], 'lookup ok')
        self.assertEqual(response.content, b'rendered')
